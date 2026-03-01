/**
 * Sample C++ code for Joern CPG analysis testing
 * Demonstrates: classes, inheritance, templates, virtual functions
 */

#include <iostream>
#include <string>
#include <vector>
#include <memory>

// Abstract base class
class Shape {
public:
    virtual ~Shape() = default;
    virtual double area() const = 0;
    virtual double perimeter() const = 0;
    virtual std::string name() const = 0;
};

// Rectangle class
class Rectangle : public Shape {
private:
    double width_;
    double height_;

public:
    Rectangle(double width, double height)
        : width_(width), height_(height) {}

    double area() const override {
        return width_ * height_;
    }

    double perimeter() const override {
        return 2 * (width_ + height_);
    }

    std::string name() const override {
        return "Rectangle";
    }

    double width() const { return width_; }
    double height() const { return height_; }
};

// Circle class
class Circle : public Shape {
private:
    double radius_;
    static constexpr double PI = 3.14159265358979;

public:
    explicit Circle(double radius) : radius_(radius) {}

    double area() const override {
        return PI * radius_ * radius_;
    }

    double perimeter() const override {
        return 2 * PI * radius_;
    }

    std::string name() const override {
        return "Circle";
    }

    double radius() const { return radius_; }
};

// Template function
template<typename T>
T max_value(T a, T b) {
    return (a > b) ? a : b;
}

// Shape collection manager
class ShapeManager {
private:
    std::vector<std::unique_ptr<Shape>> shapes_;

public:
    void addShape(std::unique_ptr<Shape> shape) {
        shapes_.push_back(std::move(shape));
    }

    double totalArea() const {
        double total = 0.0;
        for (const auto& shape : shapes_) {
            total += shape->area();
        }
        return total;
    }

    void printAll() const {
        for (const auto& shape : shapes_) {
            std::cout << shape->name() << ": area=" << shape->area()
                      << ", perimeter=" << shape->perimeter() << std::endl;
        }
    }
};

int main() {
    ShapeManager manager;

    manager.addShape(std::make_unique<Rectangle>(5.0, 3.0));
    manager.addShape(std::make_unique<Circle>(2.5));
    manager.addShape(std::make_unique<Rectangle>(4.0, 4.0));

    manager.printAll();
    std::cout << "Total area: " << manager.totalArea() << std::endl;

    std::cout << "Max of 10, 20: " << max_value(10, 20) << std::endl;
    std::cout << "Max of 3.14, 2.71: " << max_value(3.14, 2.71) << std::endl;

    return 0;
}
