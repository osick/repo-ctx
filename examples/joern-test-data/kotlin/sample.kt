/**
 * Sample Kotlin code for Joern CPG analysis testing
 * Demonstrates: classes, interfaces, data classes, coroutines, extension functions
 */

package com.example.shapes

import kotlinx.coroutines.*

// Shape interface
interface Shape {
    val name: String
    fun area(): Double
    fun perimeter(): Double

    fun printInfo(): String =
        "$name: area=${"%.2f".format(area())}, perimeter=${"%.2f".format(perimeter())}"
}

// Abstract base class
abstract class AbstractShape(var color: String = "white") : Shape

// Rectangle class
class Rectangle(
    val width: Double,
    val height: Double,
    color: String = "white"
) : AbstractShape(color) {

    override val name: String get() = "Rectangle"

    override fun area(): Double = width * height

    override fun perimeter(): Double = 2 * (width + height)

    fun isSquare(): Boolean = kotlin.math.abs(width - height) < 0.0001
}

// Circle class
class Circle(
    val radius: Double,
    color: String = "white"
) : AbstractShape(color) {

    companion object {
        const val PI = 3.14159265358979
    }

    override val name: String get() = "Circle"

    val diameter: Double get() = 2 * radius

    override fun area(): Double = PI * radius * radius

    override fun perimeter(): Double = 2 * PI * radius
}

// Data class for immutable shape records
data class ShapeRecord(
    val name: String,
    val area: Double,
    val perimeter: Double
)

// Extension function for shapes
fun Shape.toRecord(): ShapeRecord = ShapeRecord(name, area(), perimeter())

// Generic shape manager
class ShapeManager<T : Shape> {
    private val shapes = mutableListOf<T>()

    fun addShape(shape: T): ShapeManager<T> {
        shapes.add(shape)
        return this // Enable chaining
    }

    fun totalArea(): Double = shapes.sumOf { it.area() }

    fun totalPerimeter(): Double = shapes.sumOf { it.perimeter() }

    inline fun filter(predicate: (T) -> Boolean): List<T> =
        shapes.filter(predicate)

    fun findByColor(color: String): List<T> =
        shapes.filter { (it as? AbstractShape)?.color == color }

    fun printAll() {
        shapes.forEach { println(it.printInfo()) }
    }

    fun toRecords(): List<ShapeRecord> =
        shapes.map { it.toRecord() }

    // Coroutine-based async processing
    suspend fun processAsync(): List<String> = coroutineScope {
        shapes.map { shape ->
            async {
                delay(10) // Simulate async work
                "Processed: ${shape.printInfo()}"
            }
        }.awaitAll()
    }
}

// Factory object with DSL
object ShapeFactory {
    private var createdCount = 0

    fun createRectangle(width: Double, height: Double, color: String = "white"): Rectangle {
        require(width > 0 && height > 0) { "Dimensions must be positive" }
        createdCount++
        return Rectangle(width, height, color)
    }

    fun createCircle(radius: Double, color: String = "white"): Circle {
        require(radius > 0) { "Radius must be positive" }
        createdCount++
        return Circle(radius, color)
    }

    val totalCreated: Int get() = createdCount
}

// DSL builder for shapes
class ShapeBuilder {
    private val shapes = mutableListOf<Shape>()

    fun rectangle(width: Double, height: Double, color: String = "white") {
        shapes.add(Rectangle(width, height, color))
    }

    fun circle(radius: Double, color: String = "white") {
        shapes.add(Circle(radius, color))
    }

    fun build(): List<Shape> = shapes.toList()
}

fun shapes(init: ShapeBuilder.() -> Unit): List<Shape> =
    ShapeBuilder().apply(init).build()

// Sealed class for shape operations result
sealed class ShapeResult<out T> {
    data class Success<T>(val value: T) : ShapeResult<T>()
    data class Error(val message: String) : ShapeResult<Nothing>()
}

// Main function
fun main() = runBlocking {
    val manager = ShapeManager<Shape>()

    manager
        .addShape(ShapeFactory.createRectangle(5.0, 3.0, "red"))
        .addShape(ShapeFactory.createCircle(2.5, "blue"))
        .addShape(ShapeFactory.createRectangle(4.0, 4.0, "red"))

    println("All shapes:")
    manager.printAll()

    println("\nTotal area: ${"%.2f".format(manager.totalArea())}")
    println("Total perimeter: ${"%.2f".format(manager.totalPerimeter())}")

    // Filtering with lambda
    val largeShapes = manager.filter { it.area() > 15 }
    println("\nLarge shapes (area > 15):")
    largeShapes.forEach { println("  ${it.printInfo()}") }

    // Find by color
    val redShapes = manager.findByColor("red")
    println("\nRed shapes:")
    redShapes.forEach { println("  ${it.printInfo()}") }

    // Async processing
    println("\nAsync processing:")
    val results = manager.processAsync()
    results.forEach { println("  $it") }

    println("\nFactory created ${ShapeFactory.totalCreated} shapes")

    // Using DSL
    println("\nShapes created with DSL:")
    val dslShapes = shapes {
        rectangle(2.0, 3.0, "green")
        circle(1.5, "yellow")
    }
    dslShapes.forEach { println("  ${it.printInfo()}") }
}
