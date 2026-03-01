'From Squeak6.0 of 1 January 2024 [latest update: #12345] on 7 December 2025 at 10:00:00 am'!

!Object methodsFor: 'testing' stamp: 'author 12/7/2025 10:00'!
isShape
	"Return whether the receiver is a Shape"
	^ false! !

Object subclass: #Shape
	instanceVariableNames: 'color'
	classVariableNames: ''
	poolDictionaries: ''
	category: 'Shapes-Core'!

!Shape commentStamp: 'author 12/7/2025 10:00' prior: 0!
Abstract base class for geometric shapes.
Provides common interface for area and perimeter calculations.!

!Shape methodsFor: 'accessing' stamp: 'author 12/7/2025 10:00'!
color
	"Return the color of this shape"
	^ color! !

!Shape methodsFor: 'accessing' stamp: 'author 12/7/2025 10:00'!
color: aColor
	"Set the color of this shape"
	color := aColor! !

!Shape methodsFor: 'computing' stamp: 'author 12/7/2025 10:00'!
area
	"Return the area of this shape - subclass responsibility"
	self subclassResponsibility! !

!Shape methodsFor: 'computing' stamp: 'author 12/7/2025 10:00'!
perimeter
	"Return the perimeter of this shape - subclass responsibility"
	self subclassResponsibility! !

!Shape methodsFor: 'printing' stamp: 'author 12/7/2025 10:00'!
printOn: aStream
	"Print a description of this shape"
	aStream
		nextPutAll: self class name;
		nextPutAll: ' (';
		nextPutAll: color asString;
		nextPut: $)! !

!Shape methodsFor: 'testing' stamp: 'author 12/7/2025 10:00'!
isShape
	"Return whether the receiver is a Shape"
	^ true! !

Shape subclass: #Circle
	instanceVariableNames: 'radius'
	classVariableNames: 'Pi'
	poolDictionaries: ''
	category: 'Shapes-Geometry'!

!Circle class methodsFor: 'class initialization' stamp: 'author 12/7/2025 10:00'!
initialize
	"Initialize class variables"
	Pi := Float pi! !

!Circle class methodsFor: 'instance creation' stamp: 'author 12/7/2025 10:00'!
radius: aNumber color: aColor
	"Create a new circle with the given radius and color"
	^ self new
		radius: aNumber;
		color: aColor;
		yourself! !

!Circle methodsFor: 'accessing' stamp: 'author 12/7/2025 10:00'!
radius
	"Return the radius of this circle"
	^ radius! !

!Circle methodsFor: 'accessing' stamp: 'author 12/7/2025 10:00'!
radius: aNumber
	"Set the radius of this circle"
	radius := aNumber! !

!Circle methodsFor: 'computing' stamp: 'author 12/7/2025 10:00'!
area
	"Return the area of this circle (pi * r^2)"
	^ Pi * radius * radius! !

!Circle methodsFor: 'computing' stamp: 'author 12/7/2025 10:00'!
perimeter
	"Return the perimeter (circumference) of this circle (2 * pi * r)"
	^ 2 * Pi * radius! !

!Circle methodsFor: 'computing' stamp: 'author 12/7/2025 10:00'!
diameter
	"Return the diameter of this circle"
	^ radius * 2! !

Shape subclass: #Rectangle
	instanceVariableNames: 'width height'
	classVariableNames: ''
	poolDictionaries: ''
	category: 'Shapes-Geometry'!

!Rectangle class methodsFor: 'instance creation' stamp: 'author 12/7/2025 10:00'!
width: w height: h color: aColor
	"Create a new rectangle with the given dimensions and color"
	^ self new
		width: w;
		height: h;
		color: aColor;
		yourself! !

!Rectangle methodsFor: 'accessing' stamp: 'author 12/7/2025 10:00'!
width
	"Return the width of this rectangle"
	^ width! !

!Rectangle methodsFor: 'accessing' stamp: 'author 12/7/2025 10:00'!
width: aNumber
	"Set the width of this rectangle"
	width := aNumber! !

!Rectangle methodsFor: 'accessing' stamp: 'author 12/7/2025 10:00'!
height
	"Return the height of this rectangle"
	^ height! !

!Rectangle methodsFor: 'accessing' stamp: 'author 12/7/2025 10:00'!
height: aNumber
	"Set the height of this rectangle"
	height := aNumber! !

!Rectangle methodsFor: 'computing' stamp: 'author 12/7/2025 10:00'!
area
	"Return the area of this rectangle (width * height)"
	^ width * height! !

!Rectangle methodsFor: 'computing' stamp: 'author 12/7/2025 10:00'!
perimeter
	"Return the perimeter of this rectangle (2 * (width + height))"
	^ 2 * (width + height)! !

!Rectangle methodsFor: 'testing' stamp: 'author 12/7/2025 10:00'!
isSquare
	"Return whether this rectangle is a square"
	^ width = height! !

Rectangle subclass: #Square
	instanceVariableNames: ''
	classVariableNames: ''
	poolDictionaries: ''
	category: 'Shapes-Geometry'!

!Square class methodsFor: 'instance creation' stamp: 'author 12/7/2025 10:00'!
side: aNumber color: aColor
	"Create a new square with the given side length and color"
	^ self new
		width: aNumber;
		height: aNumber;
		color: aColor;
		yourself! !

!Square methodsFor: 'accessing' stamp: 'author 12/7/2025 10:00'!
side
	"Return the side length of this square"
	^ width! !

!Square methodsFor: 'accessing' stamp: 'author 12/7/2025 10:00'!
side: aNumber
	"Set the side length of this square"
	width := aNumber.
	height := aNumber! !

Object subclass: #ShapeCollection
	instanceVariableNames: 'shapes'
	classVariableNames: ''
	poolDictionaries: ''
	category: 'Shapes-Collections'!

!ShapeCollection methodsFor: 'initialization' stamp: 'author 12/7/2025 10:00'!
initialize
	"Initialize an empty shape collection"
	super initialize.
	shapes := OrderedCollection new! !

!ShapeCollection methodsFor: 'adding' stamp: 'author 12/7/2025 10:00'!
add: aShape
	"Add a shape to the collection"
	shapes add: aShape.
	^ aShape! !

!ShapeCollection methodsFor: 'enumerating' stamp: 'author 12/7/2025 10:00'!
do: aBlock
	"Iterate over all shapes"
	shapes do: aBlock! !

!ShapeCollection methodsFor: 'computing' stamp: 'author 12/7/2025 10:00'!
totalArea
	"Return the sum of all shape areas"
	^ shapes inject: 0 into: [:sum :shape | sum + shape area]! !

!ShapeCollection methodsFor: 'querying' stamp: 'author 12/7/2025 10:00'!
selectByColor: aColor
	"Return shapes matching the given color"
	^ shapes select: [:shape | shape color = aColor]! !
