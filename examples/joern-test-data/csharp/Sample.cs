// Sample C# code for Joern CPG analysis testing
// Demonstrates: classes, interfaces, generics, LINQ, async/await

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace App.Shapes
{
    // Shape interface
    public interface IShape
    {
        string Name { get; }
        double Area();
        double Perimeter();
    }

    // Extension methods
    public static class ShapeExtensions
    {
        public static string PrintInfo(this IShape shape)
        {
            return $"{shape.Name}: area={shape.Area():F2}, perimeter={shape.Perimeter():F2}";
        }
    }

    // Abstract base class
    public abstract class Shape : IShape
    {
        public string Color { get; set; } = "white";

        public abstract string Name { get; }
        public abstract double Area();
        public abstract double Perimeter();
    }

    // Rectangle class
    public class Rectangle : Shape
    {
        public double Width { get; }
        public double Height { get; }

        public Rectangle(double width, double height)
        {
            Width = width;
            Height = height;
        }

        public override string Name => "Rectangle";

        public override double Area() => Width * Height;

        public override double Perimeter() => 2 * (Width + Height);

        public bool IsSquare => Math.Abs(Width - Height) < 0.0001;
    }

    // Circle class
    public class Circle : Shape
    {
        private const double Pi = 3.14159265358979;

        public double Radius { get; }

        public Circle(double radius)
        {
            Radius = radius;
        }

        public override string Name => "Circle";

        public override double Area() => Pi * Radius * Radius;

        public override double Perimeter() => 2 * Pi * Radius;

        public double Diameter => 2 * Radius;
    }

    // Generic shape manager
    public class ShapeManager<T> where T : IShape
    {
        private readonly List<T> _shapes = new();

        public void AddShape(T shape)
        {
            _shapes.Add(shape);
        }

        public double TotalArea() => _shapes.Sum(s => s.Area());

        public double TotalPerimeter() => _shapes.Sum(s => s.Perimeter());

        public IEnumerable<T> Filter(Func<T, bool> predicate)
        {
            return _shapes.Where(predicate);
        }

        public void PrintAll()
        {
            foreach (var shape in _shapes)
            {
                Console.WriteLine(shape.PrintInfo());
            }
        }

        // Async processing
        public async Task<List<string>> ProcessAsync()
        {
            var tasks = _shapes.Select(async shape =>
            {
                await Task.Delay(10); // Simulate async work
                return shape.PrintInfo();
            });

            return (await Task.WhenAll(tasks)).ToList();
        }
    }

    // Record type (C# 9+)
    public record ShapeRecord(string Name, double Area, double Perimeter);

    // Main program
    public class Program
    {
        public static async Task Main(string[] args)
        {
            var manager = new ShapeManager<IShape>();

            manager.AddShape(new Rectangle(5.0, 3.0) { Color = "red" });
            manager.AddShape(new Circle(2.5) { Color = "blue" });
            manager.AddShape(new Rectangle(4.0, 4.0) { Color = "red" });

            Console.WriteLine("All shapes:");
            manager.PrintAll();

            Console.WriteLine($"\nTotal area: {manager.TotalArea():F2}");
            Console.WriteLine($"Total perimeter: {manager.TotalPerimeter():F2}");

            // LINQ filtering
            var largeShapes = manager.Filter(s => s.Area() > 15);
            Console.WriteLine("\nLarge shapes (area > 15):");
            foreach (var shape in largeShapes)
            {
                Console.WriteLine($"  {shape.PrintInfo()}");
            }

            // Async processing
            Console.WriteLine("\nAsync processing:");
            var results = await manager.ProcessAsync();
            foreach (var result in results)
            {
                Console.WriteLine($"  Processed: {result}");
            }
        }
    }
}
