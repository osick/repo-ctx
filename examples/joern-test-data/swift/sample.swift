// Sample Swift code for Joern CPG analysis testing
// Demonstrates: protocols, classes, structs, extensions, generics

import Foundation

// Shape protocol
protocol Shape {
    var name: String { get }
    func area() -> Double
    func perimeter() -> Double
}

// Printable protocol extension
extension Shape {
    func printInfo() -> String {
        return "\(name): area=\(String(format: "%.2f", area())), perimeter=\(String(format: "%.2f", perimeter()))"
    }
}

// Rectangle struct
struct Rectangle: Shape {
    let width: Double
    let height: Double

    var name: String { "Rectangle" }

    func area() -> Double {
        return width * height
    }

    func perimeter() -> Double {
        return 2 * (width + height)
    }

    var isSquare: Bool {
        return width == height
    }
}

// Circle struct
struct Circle: Shape {
    static let pi: Double = 3.14159265358979
    let radius: Double

    var name: String { "Circle" }

    func area() -> Double {
        return Circle.pi * radius * radius
    }

    func perimeter() -> Double {
        return 2 * Circle.pi * radius
    }

    var diameter: Double {
        return 2 * radius
    }
}

// Generic container class
class ShapeManager<T: Shape> {
    private var shapes: [T] = []

    func addShape(_ shape: T) {
        shapes.append(shape)
    }

    func totalArea() -> Double {
        return shapes.reduce(0.0) { $0 + $1.area() }
    }

    func totalPerimeter() -> Double {
        return shapes.reduce(0.0) { $0 + $1.perimeter() }
    }

    func forEach(_ action: (T) -> Void) {
        shapes.forEach(action)
    }

    func printAll() {
        shapes.forEach { print($0.printInfo()) }
    }
}

// Result type for error handling
enum ShapeError: Error {
    case invalidDimension(String)
    case negativeValue
}

// Factory with error handling
class ShapeFactory {
    static func createRectangle(width: Double, height: Double) throws -> Rectangle {
        guard width > 0, height > 0 else {
            throw ShapeError.invalidDimension("Width and height must be positive")
        }
        return Rectangle(width: width, height: height)
    }

    static func createCircle(radius: Double) throws -> Circle {
        guard radius > 0 else {
            throw ShapeError.negativeValue
        }
        return Circle(radius: radius)
    }
}

// Async processing (Swift 5.5+)
actor ShapeProcessor {
    private var processedCount: Int = 0

    func process(_ shape: Shape) async -> String {
        processedCount += 1
        return "Processed #\(processedCount): \(shape.printInfo())"
    }

    func getProcessedCount() -> Int {
        return processedCount
    }
}

// Main execution
@main
struct Main {
    static func main() async {
        // Using ShapeManager with any Shape
        let anyManager = ShapeManager<any Shape>()
        anyManager.addShape(Rectangle(width: 5.0, height: 3.0))
        anyManager.addShape(Circle(radius: 2.5))
        anyManager.addShape(Rectangle(width: 4.0, height: 4.0))

        print("All shapes:")
        anyManager.printAll()

        print("\nTotal area: \(String(format: "%.2f", anyManager.totalArea()))")
        print("Total perimeter: \(String(format: "%.2f", anyManager.totalPerimeter()))")

        // Using factory with error handling
        do {
            let rect = try ShapeFactory.createRectangle(width: 10, height: 5)
            print("\nCreated via factory: \(rect.printInfo())")
        } catch ShapeError.invalidDimension(let message) {
            print("Error: \(message)")
        } catch {
            print("Unknown error: \(error)")
        }

        // Async processing
        let processor = ShapeProcessor()
        let result = await processor.process(Circle(radius: 3.0))
        print("\n\(result)")
    }
}
