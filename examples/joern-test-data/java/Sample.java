/**
 * Sample Java code for Joern CPG analysis testing
 * Demonstrates: classes, interfaces, generics, streams, records
 */

package com.example.shapes;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.function.Predicate;
import java.util.stream.Collectors;

// Shape interface
interface Shape {
    String getName();
    double area();
    double perimeter();

    default String printInfo() {
        return String.format("%s: area=%.2f, perimeter=%.2f",
                getName(), area(), perimeter());
    }
}

// Abstract base class
abstract class AbstractShape implements Shape {
    private String color = "white";

    public String getColor() {
        return color;
    }

    public void setColor(String color) {
        this.color = color;
    }
}

// Rectangle class
class Rectangle extends AbstractShape {
    private final double width;
    private final double height;

    public Rectangle(double width, double height) {
        this.width = width;
        this.height = height;
    }

    @Override
    public String getName() {
        return "Rectangle";
    }

    public double getWidth() {
        return width;
    }

    public double getHeight() {
        return height;
    }

    @Override
    public double area() {
        return width * height;
    }

    @Override
    public double perimeter() {
        return 2 * (width + height);
    }

    public boolean isSquare() {
        return Math.abs(width - height) < 0.0001;
    }
}

// Circle class
class Circle extends AbstractShape {
    private static final double PI = 3.14159265358979;
    private final double radius;

    public Circle(double radius) {
        this.radius = radius;
    }

    @Override
    public String getName() {
        return "Circle";
    }

    public double getRadius() {
        return radius;
    }

    public double getDiameter() {
        return 2 * radius;
    }

    @Override
    public double area() {
        return PI * radius * radius;
    }

    @Override
    public double perimeter() {
        return 2 * PI * radius;
    }
}

// Record for immutable shape data (Java 16+)
record ShapeRecord(String name, double area, double perimeter) {}

// Generic shape manager
class ShapeManager<T extends Shape> {
    private final List<T> shapes = new ArrayList<>();

    public ShapeManager<T> addShape(T shape) {
        shapes.add(shape);
        return this; // Enable chaining
    }

    public double totalArea() {
        return shapes.stream()
                .mapToDouble(Shape::area)
                .sum();
    }

    public double totalPerimeter() {
        return shapes.stream()
                .mapToDouble(Shape::perimeter)
                .sum();
    }

    public List<T> filter(Predicate<T> predicate) {
        return shapes.stream()
                .filter(predicate)
                .collect(Collectors.toList());
    }

    public List<T> findByColor(String color) {
        return shapes.stream()
                .filter(s -> s instanceof AbstractShape)
                .filter(s -> ((AbstractShape) s).getColor().equals(color))
                .collect(Collectors.toList());
    }

    public void printAll() {
        shapes.forEach(shape -> System.out.println(shape.printInfo()));
    }

    public List<ShapeRecord> toRecords() {
        return shapes.stream()
                .map(s -> new ShapeRecord(s.getName(), s.area(), s.perimeter()))
                .collect(Collectors.toList());
    }

    // Async processing
    public CompletableFuture<List<String>> processAsync() {
        List<CompletableFuture<String>> futures = shapes.stream()
                .map(shape -> CompletableFuture.supplyAsync(() -> {
                    try {
                        Thread.sleep(10); // Simulate async work
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                    return "Processed: " + shape.printInfo();
                }))
                .collect(Collectors.toList());

        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
                .thenApply(v -> futures.stream()
                        .map(CompletableFuture::join)
                        .collect(Collectors.toList()));
    }
}

// Factory class
class ShapeFactory {
    private int createdCount = 0;

    public Rectangle createRectangle(double width, double height, String color) {
        if (width <= 0 || height <= 0) {
            throw new IllegalArgumentException("Dimensions must be positive");
        }
        createdCount++;
        Rectangle rect = new Rectangle(width, height);
        rect.setColor(color);
        return rect;
    }

    public Circle createCircle(double radius, String color) {
        if (radius <= 0) {
            throw new IllegalArgumentException("Radius must be positive");
        }
        createdCount++;
        Circle circle = new Circle(radius);
        circle.setColor(color);
        return circle;
    }

    public int getCreatedCount() {
        return createdCount;
    }
}

// Main class
public class Sample {
    public static void main(String[] args) {
        ShapeManager<Shape> manager = new ShapeManager<>();
        ShapeFactory factory = new ShapeFactory();

        manager
                .addShape(factory.createRectangle(5.0, 3.0, "red"))
                .addShape(factory.createCircle(2.5, "blue"))
                .addShape(factory.createRectangle(4.0, 4.0, "red"));

        System.out.println("All shapes:");
        manager.printAll();

        System.out.printf("%nTotal area: %.2f%n", manager.totalArea());
        System.out.printf("Total perimeter: %.2f%n", manager.totalPerimeter());

        // Filtering with lambda
        List<Shape> largeShapes = manager.filter(s -> s.area() > 15);
        System.out.println("\nLarge shapes (area > 15):");
        largeShapes.forEach(s -> System.out.println("  " + s.printInfo()));

        // Find by color
        List<Shape> redShapes = manager.findByColor("red");
        System.out.println("\nRed shapes:");
        redShapes.forEach(s -> System.out.println("  " + s.printInfo()));

        // Async processing
        System.out.println("\nAsync processing:");
        manager.processAsync()
                .thenAccept(results -> results.forEach(r -> System.out.println("  " + r)))
                .join();

        System.out.printf("%nFactory created %d shapes%n", factory.getCreatedCount());
    }
}
