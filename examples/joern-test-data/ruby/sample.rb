# Sample Ruby code for Joern CPG analysis testing
# Demonstrates: classes, modules, mixins, blocks, lambdas

# Shape module with shared functionality
module Printable
  def print_info
    "#{name}: area=#{area.round(2)}, perimeter=#{perimeter.round(2)}"
  end
end

# Abstract-like base class
class Shape
  include Printable

  attr_accessor :color

  def initialize(color = 'white')
    @color = color
  end

  def area
    raise NotImplementedError, 'Subclasses must implement area'
  end

  def perimeter
    raise NotImplementedError, 'Subclasses must implement perimeter'
  end

  def name
    self.class.name
  end
end

# Rectangle class
class Rectangle < Shape
  attr_reader :width, :height

  def initialize(width, height, color = 'white')
    super(color)
    @width = width
    @height = height
  end

  def area
    @width * @height
  end

  def perimeter
    2 * (@width + @height)
  end

  def square?
    @width == @height
  end
end

# Circle class
class Circle < Shape
  PI = 3.14159265358979

  attr_reader :radius

  def initialize(radius, color = 'white')
    super(color)
    @radius = radius
  end

  def area
    PI * @radius ** 2
  end

  def perimeter
    2 * PI * @radius
  end

  def diameter
    2 * @radius
  end
end

# ShapeManager with functional programming features
class ShapeManager
  def initialize
    @shapes = []
  end

  def add_shape(shape)
    @shapes << shape
    self
  end

  def total_area
    @shapes.reduce(0.0) { |sum, shape| sum + shape.area }
  end

  def total_perimeter
    @shapes.sum(&:perimeter)
  end

  def each(&block)
    @shapes.each(&block)
  end

  def map(&block)
    @shapes.map(&block)
  end

  def select(&block)
    @shapes.select(&block)
  end

  def find_by_color(color)
    select { |shape| shape.color == color }
  end

  def print_all
    each { |shape| puts shape.print_info }
  end

  # Lambda for custom filtering
  def filter_by(&predicate)
    @shapes.select(&predicate)
  end
end

# Main execution
if __FILE__ == $PROGRAM_NAME
  manager = ShapeManager.new

  manager
    .add_shape(Rectangle.new(5.0, 3.0, 'red'))
    .add_shape(Circle.new(2.5, 'blue'))
    .add_shape(Rectangle.new(4.0, 4.0, 'red'))

  puts 'All shapes:'
  manager.print_all

  puts "\nTotal area: #{manager.total_area.round(2)}"
  puts "Total perimeter: #{manager.total_perimeter.round(2)}"

  # Using lambda for filtering
  large_shapes = manager.filter_by { |s| s.area > 15 }
  puts "\nLarge shapes (area > 15):"
  large_shapes.each { |s| puts "  #{s.print_info}" }

  # Find red shapes
  red_shapes = manager.find_by_color('red')
  puts "\nRed shapes:"
  red_shapes.each { |s| puts "  #{s.print_info}" }
end
