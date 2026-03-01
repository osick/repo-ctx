"""
Sample Python code for Joern CPG analysis testing
Demonstrates: classes, inheritance, decorators, type hints, async
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Callable, TypeVar
import asyncio
import math

# Type variable for generics
T = TypeVar('T', bound='Shape')


# Abstract base class
class Shape(ABC):
    """Abstract base class for shapes."""

    def __init__(self, color: str = "white"):
        self._color = color

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, value: str) -> None:
        self._color = value

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the shape."""
        pass

    @abstractmethod
    def area(self) -> float:
        """Calculate the area of the shape."""
        pass

    @abstractmethod
    def perimeter(self) -> float:
        """Calculate the perimeter of the shape."""
        pass

    def print_info(self) -> str:
        """Return formatted shape information."""
        return f"{self.name}: area={self.area():.2f}, perimeter={self.perimeter():.2f}"


# Rectangle class
class Rectangle(Shape):
    """Rectangle shape implementation."""

    def __init__(self, width: float, height: float, color: str = "white"):
        super().__init__(color)
        self._width = width
        self._height = height

    @property
    def name(self) -> str:
        return "Rectangle"

    @property
    def width(self) -> float:
        return self._width

    @property
    def height(self) -> float:
        return self._height

    def area(self) -> float:
        return self._width * self._height

    def perimeter(self) -> float:
        return 2 * (self._width + self._height)

    def is_square(self) -> bool:
        return abs(self._width - self._height) < 0.0001


# Circle class
class Circle(Shape):
    """Circle shape implementation."""

    def __init__(self, radius: float, color: str = "white"):
        super().__init__(color)
        self._radius = radius

    @property
    def name(self) -> str:
        return "Circle"

    @property
    def radius(self) -> float:
        return self._radius

    def area(self) -> float:
        return math.pi * self._radius ** 2

    def perimeter(self) -> float:
        return 2 * math.pi * self._radius

    @property
    def diameter(self) -> float:
        return 2 * self._radius


# Dataclass for shape records
@dataclass
class ShapeRecord:
    """Immutable shape record."""
    name: str
    area: float
    perimeter: float


# Shape manager with functional features
class ShapeManager:
    """Manager for shape collections."""

    def __init__(self):
        self._shapes: List[Shape] = []

    def add_shape(self, shape: Shape) -> "ShapeManager":
        """Add a shape and return self for chaining."""
        self._shapes.append(shape)
        return self

    def total_area(self) -> float:
        """Calculate total area of all shapes."""
        return sum(shape.area() for shape in self._shapes)

    def total_perimeter(self) -> float:
        """Calculate total perimeter of all shapes."""
        return sum(shape.perimeter() for shape in self._shapes)

    def filter_by(self, predicate: Callable[[Shape], bool]) -> List[Shape]:
        """Filter shapes by predicate."""
        return [s for s in self._shapes if predicate(s)]

    def find_by_color(self, color: str) -> List[Shape]:
        """Find shapes by color."""
        return self.filter_by(lambda s: s.color == color)

    def print_all(self) -> None:
        """Print all shapes."""
        for shape in self._shapes:
            print(shape.print_info())

    def to_records(self) -> List[ShapeRecord]:
        """Convert shapes to immutable records."""
        return [
            ShapeRecord(s.name, s.area(), s.perimeter())
            for s in self._shapes
        ]

    # Async processing
    async def process_async(self) -> List[str]:
        """Process shapes asynchronously."""
        async def process_shape(shape: Shape) -> str:
            await asyncio.sleep(0.01)  # Simulate async work
            return f"Processed: {shape.print_info()}"

        tasks = [process_shape(s) for s in self._shapes]
        return await asyncio.gather(*tasks)


# Decorator for logging
def log_call(func: Callable) -> Callable:
    """Decorator to log function calls."""
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__}")
        return result
    return wrapper


@log_call
def create_sample_shapes() -> ShapeManager:
    """Create sample shapes."""
    manager = ShapeManager()
    manager.add_shape(Rectangle(5.0, 3.0, "red"))
    manager.add_shape(Circle(2.5, "blue"))
    manager.add_shape(Rectangle(4.0, 4.0, "red"))
    return manager


async def main():
    """Main async function."""
    manager = create_sample_shapes()

    print("\nAll shapes:")
    manager.print_all()

    print(f"\nTotal area: {manager.total_area():.2f}")
    print(f"Total perimeter: {manager.total_perimeter():.2f}")

    # Filtering
    large_shapes = manager.filter_by(lambda s: s.area() > 15)
    print("\nLarge shapes (area > 15):")
    for shape in large_shapes:
        print(f"  {shape.print_info()}")

    # Find by color
    red_shapes = manager.find_by_color("red")
    print("\nRed shapes:")
    for shape in red_shapes:
        print(f"  {shape.print_info()}")

    # Async processing
    print("\nAsync processing:")
    results = await manager.process_async()
    for result in results:
        print(f"  {result}")


if __name__ == "__main__":
    asyncio.run(main())
