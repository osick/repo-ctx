/**
 * Sample JavaScript code for Joern CPG analysis testing
 * Demonstrates: classes, inheritance, async/await, closures, modules
 */

// Shape base class
class Shape {
  #color;

  constructor(color = 'white') {
    this.#color = color;
  }

  get color() {
    return this.#color;
  }

  set color(value) {
    this.#color = value;
  }

  get name() {
    throw new Error('Subclasses must implement name');
  }

  area() {
    throw new Error('Subclasses must implement area()');
  }

  perimeter() {
    throw new Error('Subclasses must implement perimeter()');
  }

  printInfo() {
    return `${this.name}: area=${this.area().toFixed(2)}, perimeter=${this.perimeter().toFixed(2)}`;
  }
}

// Rectangle class
class Rectangle extends Shape {
  #width;
  #height;

  constructor(width, height, color = 'white') {
    super(color);
    this.#width = width;
    this.#height = height;
  }

  get name() {
    return 'Rectangle';
  }

  get width() {
    return this.#width;
  }

  get height() {
    return this.#height;
  }

  area() {
    return this.#width * this.#height;
  }

  perimeter() {
    return 2 * (this.#width + this.#height);
  }

  isSquare() {
    return Math.abs(this.#width - this.#height) < 0.0001;
  }
}

// Circle class
class Circle extends Shape {
  static PI = 3.14159265358979;

  #radius;

  constructor(radius, color = 'white') {
    super(color);
    this.#radius = radius;
  }

  get name() {
    return 'Circle';
  }

  get radius() {
    return this.#radius;
  }

  get diameter() {
    return 2 * this.#radius;
  }

  area() {
    return Circle.PI * this.#radius ** 2;
  }

  perimeter() {
    return 2 * Circle.PI * this.#radius;
  }
}

// ShapeManager class with functional features
class ShapeManager {
  #shapes = [];

  addShape(shape) {
    this.#shapes.push(shape);
    return this; // Enable chaining
  }

  totalArea() {
    return this.#shapes.reduce((sum, shape) => sum + shape.area(), 0);
  }

  totalPerimeter() {
    return this.#shapes.reduce((sum, shape) => sum + shape.perimeter(), 0);
  }

  filter(predicate) {
    return this.#shapes.filter(predicate);
  }

  findByColor(color) {
    return this.filter((shape) => shape.color === color);
  }

  forEach(callback) {
    this.#shapes.forEach(callback);
  }

  map(callback) {
    return this.#shapes.map(callback);
  }

  printAll() {
    this.forEach((shape) => console.log(shape.printInfo()));
  }

  // Async processing
  async processAsync() {
    const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

    const results = await Promise.all(
      this.#shapes.map(async (shape) => {
        await delay(10); // Simulate async work
        return `Processed: ${shape.printInfo()}`;
      })
    );

    return results;
  }
}

// Factory function with closure
function createShapeFactory() {
  let createdCount = 0;

  return {
    createRectangle(width, height, color) {
      if (width <= 0 || height <= 0) {
        throw new Error('Dimensions must be positive');
      }
      createdCount++;
      return new Rectangle(width, height, color);
    },

    createCircle(radius, color) {
      if (radius <= 0) {
        throw new Error('Radius must be positive');
      }
      createdCount++;
      return new Circle(radius, color);
    },

    getCreatedCount() {
      return createdCount;
    },
  };
}

// Higher-order function for filtering
const createAreaFilter = (minArea) => (shape) => shape.area() > minArea;

// Main execution
async function main() {
  const manager = new ShapeManager();
  const factory = createShapeFactory();

  manager
    .addShape(factory.createRectangle(5.0, 3.0, 'red'))
    .addShape(factory.createCircle(2.5, 'blue'))
    .addShape(factory.createRectangle(4.0, 4.0, 'red'));

  console.log('All shapes:');
  manager.printAll();

  console.log(`\nTotal area: ${manager.totalArea().toFixed(2)}`);
  console.log(`Total perimeter: ${manager.totalPerimeter().toFixed(2)}`);

  // Using higher-order function
  const largeShapes = manager.filter(createAreaFilter(15));
  console.log('\nLarge shapes (area > 15):');
  largeShapes.forEach((shape) => console.log(`  ${shape.printInfo()}`));

  // Find by color
  const redShapes = manager.findByColor('red');
  console.log('\nRed shapes:');
  redShapes.forEach((shape) => console.log(`  ${shape.printInfo()}`));

  // Async processing
  console.log('\nAsync processing:');
  const results = await manager.processAsync();
  results.forEach((result) => console.log(`  ${result}`));

  console.log(`\nFactory created ${factory.getCreatedCount()} shapes`);
}

main().catch(console.error);

// Export for module usage
module.exports = { Shape, Rectangle, Circle, ShapeManager, createShapeFactory };
