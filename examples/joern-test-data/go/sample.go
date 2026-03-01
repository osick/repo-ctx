// Sample Go code for Joern CPG analysis testing
// Demonstrates: structs, interfaces, methods, goroutines, channels

package main

import (
	"fmt"
	"sync"
	"time"
)

// Shape interface
type Shape interface {
	Area() float64
	Perimeter() float64
	Name() string
}

// Rectangle struct
type Rectangle struct {
	Width  float64
	Height float64
}

// Rectangle methods
func (r Rectangle) Area() float64 {
	return r.Width * r.Height
}

func (r Rectangle) Perimeter() float64 {
	return 2 * (r.Width + r.Height)
}

func (r Rectangle) Name() string {
	return "Rectangle"
}

// Circle struct
type Circle struct {
	Radius float64
}

// Circle methods
func (c Circle) Area() float64 {
	return 3.14159 * c.Radius * c.Radius
}

func (c Circle) Perimeter() float64 {
	return 2 * 3.14159 * c.Radius
}

func (c Circle) Name() string {
	return "Circle"
}

// ShapeProcessor processes shapes concurrently
type ShapeProcessor struct {
	shapes []Shape
	mu     sync.Mutex
}

// NewShapeProcessor creates a new processor
func NewShapeProcessor() *ShapeProcessor {
	return &ShapeProcessor{
		shapes: make([]Shape, 0),
	}
}

// AddShape adds a shape thread-safely
func (sp *ShapeProcessor) AddShape(s Shape) {
	sp.mu.Lock()
	defer sp.mu.Unlock()
	sp.shapes = append(sp.shapes, s)
}

// ProcessAsync processes shapes using goroutines
func (sp *ShapeProcessor) ProcessAsync() <-chan string {
	results := make(chan string, len(sp.shapes))

	var wg sync.WaitGroup
	for _, shape := range sp.shapes {
		wg.Add(1)
		go func(s Shape) {
			defer wg.Done()
			result := fmt.Sprintf("%s: area=%.2f, perimeter=%.2f",
				s.Name(), s.Area(), s.Perimeter())
			results <- result
		}(shape)
	}

	go func() {
		wg.Wait()
		close(results)
	}()

	return results
}

// TotalArea calculates total area of all shapes
func (sp *ShapeProcessor) TotalArea() float64 {
	total := 0.0
	for _, s := range sp.shapes {
		total += s.Area()
	}
	return total
}

func main() {
	processor := NewShapeProcessor()

	processor.AddShape(Rectangle{Width: 5.0, Height: 3.0})
	processor.AddShape(Circle{Radius: 2.5})
	processor.AddShape(Rectangle{Width: 4.0, Height: 4.0})

	fmt.Println("Processing shapes concurrently...")

	results := processor.ProcessAsync()

	for result := range results {
		fmt.Println(result)
	}

	fmt.Printf("Total area: %.2f\n", processor.TotalArea())

	time.Sleep(100 * time.Millisecond)
}
