<?php
/**
 * Sample PHP code for Joern CPG analysis testing
 * Demonstrates: classes, interfaces, traits, namespaces
 */

namespace App\Shapes;

// Shape interface
interface ShapeInterface
{
    public function area(): float;
    public function perimeter(): float;
    public function name(): string;
}

// Printable trait
trait Printable
{
    public function printInfo(): string
    {
        return sprintf(
            "%s: area=%.2f, perimeter=%.2f",
            $this->name(),
            $this->area(),
            $this->perimeter()
        );
    }
}

// Abstract base class
abstract class AbstractShape implements ShapeInterface
{
    use Printable;

    protected string $color = 'white';

    public function getColor(): string
    {
        return $this->color;
    }

    public function setColor(string $color): void
    {
        $this->color = $color;
    }
}

// Rectangle class
class Rectangle extends AbstractShape
{
    private float $width;
    private float $height;

    public function __construct(float $width, float $height)
    {
        $this->width = $width;
        $this->height = $height;
    }

    public function area(): float
    {
        return $this->width * $this->height;
    }

    public function perimeter(): float
    {
        return 2 * ($this->width + $this->height);
    }

    public function name(): string
    {
        return 'Rectangle';
    }

    public function getWidth(): float
    {
        return $this->width;
    }

    public function getHeight(): float
    {
        return $this->height;
    }
}

// Circle class
class Circle extends AbstractShape
{
    private const PI = 3.14159265358979;
    private float $radius;

    public function __construct(float $radius)
    {
        $this->radius = $radius;
    }

    public function area(): float
    {
        return self::PI * $this->radius ** 2;
    }

    public function perimeter(): float
    {
        return 2 * self::PI * $this->radius;
    }

    public function name(): string
    {
        return 'Circle';
    }

    public function getRadius(): float
    {
        return $this->radius;
    }
}

// Shape manager class
class ShapeManager
{
    /** @var ShapeInterface[] */
    private array $shapes = [];

    public function addShape(ShapeInterface $shape): void
    {
        $this->shapes[] = $shape;
    }

    public function totalArea(): float
    {
        return array_reduce(
            $this->shapes,
            fn($total, $shape) => $total + $shape->area(),
            0.0
        );
    }

    public function printAll(): void
    {
        foreach ($this->shapes as $shape) {
            if ($shape instanceof AbstractShape) {
                echo $shape->printInfo() . PHP_EOL;
            }
        }
    }
}

// Main execution
$manager = new ShapeManager();

$manager->addShape(new Rectangle(5.0, 3.0));
$manager->addShape(new Circle(2.5));
$manager->addShape(new Rectangle(4.0, 4.0));

$manager->printAll();
echo "Total area: " . $manager->totalArea() . PHP_EOL;
