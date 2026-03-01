"Filed out from VisualWorks 9.2 on 7 December 2025 at 10:00:00"!

Smalltalk defineClass: #Shape
	superclass: #{Core.Object}
	indexedType: #none
	private: false
	instanceVariableNames: 'color '
	classInstanceVariableNames: ''
	imports: ''
	category: 'Shapes-Core'!

!Shape class methodsFor: 'instance creation'!

newWithColor: aColor
	"Create a new shape with the given color"
	^self new color: aColor; yourself! !

!Shape methodsFor: 'accessing'!

color
	"Return the color of this shape"
	^color!

color: aColor
	"Set the color of this shape"
	color := aColor! !

!Shape methodsFor: 'computing'!

area
	"Return the area - subclass responsibility"
	self subclassResponsibility!

perimeter
	"Return the perimeter - subclass responsibility"
	self subclassResponsibility! !

!Shape methodsFor: 'printing'!

printOn: aStream
	"Print shape description"
	aStream
		nextPutAll: self class name;
		nextPutAll: ' color: ';
		print: color! !

Smalltalk defineClass: #Circle
	superclass: #{Shapes.Shape}
	indexedType: #none
	private: false
	instanceVariableNames: 'radius '
	classInstanceVariableNames: ''
	imports: ''
	category: 'Shapes-Geometry'!

Circle class
	instanceVariableNames: 'defaultColor '!

!Circle class methodsFor: 'class variables'!

defaultColor
	"Return the default color for new circles"
	^defaultColor ifNil: [defaultColor := Color blue]!

defaultColor: aColor
	"Set the default color for new circles"
	defaultColor := aColor! !

!Circle class methodsFor: 'instance creation'!

radius: aNumber
	"Create a circle with the given radius"
	^self new radius: aNumber; yourself!

radius: aNumber color: aColor
	"Create a circle with the given radius and color"
	^self new
		radius: aNumber;
		color: aColor;
		yourself! !

!Circle methodsFor: 'accessing'!

radius
	"Return the radius"
	^radius!

radius: aNumber
	"Set the radius"
	radius := aNumber! !

!Circle methodsFor: 'computing'!

area
	"Return pi * r^2"
	^Float pi * radius squared!

perimeter
	"Return 2 * pi * r"
	^2 * Float pi * radius!

diameter
	"Return 2 * r"
	^radius * 2! !

Smalltalk defineClass: #Rectangle
	superclass: #{Shapes.Shape}
	indexedType: #none
	private: false
	instanceVariableNames: 'width height '
	classInstanceVariableNames: ''
	imports: ''
	category: 'Shapes-Geometry'!

!Rectangle class methodsFor: 'instance creation'!

width: w height: h
	"Create a rectangle"
	^self new width: w; height: h; yourself!

width: w height: h color: aColor
	"Create a rectangle with color"
	^self new
		width: w;
		height: h;
		color: aColor;
		yourself! !

!Rectangle methodsFor: 'accessing'!

width
	^width!

width: aNumber
	width := aNumber!

height
	^height!

height: aNumber
	height := aNumber! !

!Rectangle methodsFor: 'computing'!

area
	^width * height!

perimeter
	^2 * (width + height)! !

!Rectangle methodsFor: 'testing'!

isSquare
	^width = height! !
