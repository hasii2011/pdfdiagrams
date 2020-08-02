
from typing import List
from typing import final
from typing import Union

from logging import Logger
from logging import getLogger

from os import sep as osSep

from pkg_resources import resource_filename

from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImageFont


from pyumldiagrams.BaseDiagram import BaseDiagram

from pyumldiagrams.Definitions import ClassDefinition
from pyumldiagrams.Definitions import EllipseDefinition
from pyumldiagrams.Definitions import Position
from pyumldiagrams.Definitions import RectangleDefinition
from pyumldiagrams.Definitions import Size
from pyumldiagrams.Definitions import UmlLineDefinition

from pyumldiagrams.image.ImageCommon import ImageCommon

from pyumldiagrams.Internal import InternalPosition
from pyumldiagrams.Internal import SeparatorPosition

from pyumldiagrams.image.ImageFormat import ImageFormat
from pyumldiagrams.image.ImageLine import ImageLine

ShapeDefinition = Union[EllipseDefinition, RectangleDefinition]


class ImageDiagram(BaseDiagram):

    RESOURCES_PACKAGE_NAME: final = 'pyumldiagrams.image.resources'
    RESOURCES_PATH:         final = f'pyumldiagrams{osSep}image{osSep}resources'

    DEFAULT_IMAGE_WIDTH:  final = 1280    # pixels
    DEFAULT_IMAGE_HEIGHT: final = 1024    # pixels

    DEFAULT_BACKGROUND_COLOR: str = 'LightYellow'
    DEFAULT_LINE_COLOR:       str = 'Black'
    DEFAULT_TEXT_COLOR:       str = 'Black'
    DEFAULT_IMAGE_FORMAT:     str = ImageFormat.PNG.value

    X_NUDGE_FACTOR: final = 4
    Y_NUDGE_FACTOR: final = 8

    def __init__(self, fileName: str, headerText: str = '', imageSize: Size = Size(width=DEFAULT_IMAGE_WIDTH, height=DEFAULT_IMAGE_HEIGHT)):
        """

        Args:
            fileName:
            headerText:
            imageSize:
        """

        super().__init__(fileName=fileName, headerText=headerText)

        self.logger: Logger = getLogger(__name__)

        self._img:   Image  = Image.new(mode='RGB',
                                        size=(imageSize.width, imageSize.height),
                                        color=ImageColor.getrgb(ImageDiagram.DEFAULT_BACKGROUND_COLOR))
        self._imgDraw: ImageDraw = ImageDraw.Draw(self._img)
        self._lineDrawer: ImageLine    = ImageLine(docWriter=self._imgDraw, diagramPadding=self._diagramPadding)

        fqPath:     str       = self.retrieveResourcePath('MonoFonto.ttf')
        self._font: ImageFont = ImageFont.truetype(fqPath)
        #
        # https://www.exiv2.org/tags.html
        #
        # TODO need to write the following EXIF TAGS
        #
        # 74  0112  Orientation    The image orientation viewed in terms of rows and columns.
        # 305 0131  Software       Name and version number of the software package(s) used to create the image
        # 316 013C  HostComputer   The computer and/or operating system in use at the time of image creation.
        # 270:      ImageDescription
        # 37510:    'UserComment'
        #

    def retrieveResourcePath(self, bareFileName: str) -> str:

        try:
            fqFileName: str = resource_filename(ImageDiagram.RESOURCES_PACKAGE_NAME, bareFileName)
        except (ValueError, Exception):
            #
            # Maybe we are in an app
            #
            from os import environ
            pathToResources: str = environ.get(f'{BaseDiagram.RESOURCE_ENV_VAR}')
            fqFileName:      str = f'{pathToResources}/{ImageDiagram.RESOURCES_PATH}/{bareFileName}'

        return fqFileName

    def drawClass(self, classDefinition: ClassDefinition):
        """
        Draw the class diagram defined by the input

        I am overriding the empty base definition

        Args:
            classDefinition:    The class definition
        """
        self._drawClassSymbol(classDefinition=classDefinition)

        position: Position = classDefinition.position
        size:     Size     = classDefinition.size

        iPos: InternalPosition = ImageCommon.toInternal(position=position, horizontalGap=self.horizontalGap, verticalGap=self.verticalGap)
        self._drawClassName(classDefinition=classDefinition, rectX=iPos.x, rectY=iPos.y, symbolWidth=size.width)
        separatorPosition: SeparatorPosition = self._drawNameSeparator(rectX=iPos.x, rectY=iPos.y, shapeWidth=size.width)

        methodReprs: BaseDiagram.MethodsRepr = self._buildMethods(classDefinition.methods)

        self._drawMethods(methodReprs=methodReprs, separatorPosition=separatorPosition)

    def drawUmlLine(self, lineDefinition: UmlLineDefinition):
        """
        Draw the inheritance, aggregation, or composition lines that describe the relationships
        between the UML classes
        I am overriding the empty base definition

        Args:
            lineDefinition:   A UML Line definition
        """
        self._lineDrawer.draw(lineDefinition=lineDefinition)

    def drawEllipse(self, definition: EllipseDefinition):
        """
        Draw a general purpose ellipse

        I am overriding the empty base definition

        Args:
            definition:     It's definition
        """
        xy = self.__toInternalCoordinates(definition=definition)
        self._imgDraw.ellipse(xy=xy, fill=None, outline=ImageDiagram.DEFAULT_LINE_COLOR, width=1)

    def drawRectangle(self, definition: RectangleDefinition):
        """
        Draw a general purpose rectangle

        I am overriding the empty base definition

        Args:
            definition:  The rectangle definition
        """

        xy = self.__toInternalCoordinates(definition=definition)
        self._imgDraw.rectangle(xy=xy, fill=None, outline=ImageDiagram.DEFAULT_LINE_COLOR, width=1)

    def write(self):
        """
        Call this method when you are done with placing the diagram onto a PDF document.
        I am overriding the empty base definition
        """
        self._img.save(self._fileName, ImageDiagram.DEFAULT_IMAGE_FORMAT)

    def _drawClassSymbol(self, classDefinition: ClassDefinition):

        imgDraw: ImageDraw = self._imgDraw

        position: Position = classDefinition.position
        size:     Size     = classDefinition.size

        iPos: InternalPosition = ImageCommon.toInternal(position=position, horizontalGap=self.horizontalGap, verticalGap=self.verticalGap)

        x0 = iPos.x
        y0 = iPos.y
        x1 = x0 + size.width
        y1 = y0 + size.height
        xy = [x0, y0, x1, y1]
        self.logger.info(f'Class Symbol {xy=}')
        imgDraw.rectangle(xy=xy, fill=None, outline=ImageDiagram.DEFAULT_LINE_COLOR, width=1)

    def _drawClassName(self, classDefinition: ClassDefinition, rectX: float, rectY: float, symbolWidth: float):

        imgDraw: ImageDraw = self._imgDraw

        nameWidth, nameHeight = imgDraw.textsize(text=classDefinition.name, font=self._font)

        textX: float = rectX + ((symbolWidth / 2) - (nameWidth / 2))
        textY: float = rectY + (self._fontSize / 2)

        xy = [textX, textY]
        self.logger.info(f'ClassName {xy=}')
        imgDraw.text(xy=xy, fill=ImageDiagram.DEFAULT_TEXT_COLOR, font=self._font, text=classDefinition.name)

    def _drawNameSeparator(self, rectX: float, rectY: float, shapeWidth: float) -> SeparatorPosition:
        """
        Draws the UML separator between the class name and the start of the class definition
        Does the computation to determine where it drew the separator

        Args:
            rectX: x position of symbol
            rectY: y position of symbol (
            shapeWidth: The width of the symbol

        Returns:  Where it drew the separator
        """
        imgDraw: ImageDraw = self._imgDraw

        separatorX: float = rectX
        separatorY: float = rectY + self._fontSize + ImageDiagram.Y_NUDGE_FACTOR

        endX: float = rectX + shapeWidth

        xy = [separatorX, separatorY, endX, separatorY]
        self.logger.info(f'Separator {xy=}')
        imgDraw.line(xy=xy, fill=ImageDiagram.DEFAULT_LINE_COLOR, width=1)

        return SeparatorPosition(separatorX, separatorY)

    def _drawMethods(self, methodReprs: BaseDiagram.MethodsRepr, separatorPosition: SeparatorPosition):

        imgDraw: ImageDraw = self._imgDraw

        x: float = separatorPosition.x + ImageDiagram.X_NUDGE_FACTOR
        y: float = separatorPosition.y + ImageDiagram.Y_NUDGE_FACTOR

        for methodRepr in methodReprs:

            xy = [x, y]
            imgDraw.text(xy=xy, fill=ImageDiagram.DEFAULT_TEXT_COLOR, font=self._font, text=methodRepr)
            y = y + self._fontSize + 2

    def __toInternalCoordinates(self, definition: ShapeDefinition) -> List[float]:

        pos:  Position = definition.position
        size: Size     = definition.size

        internalStart: InternalPosition = self.__toInternal(position=pos)
        internalEnd:   InternalPosition = self.__toInternal(position=Position(x=pos.x + size.width, y=pos.y + size.height))

        x1 = internalStart.x
        y1 = internalStart.y
        x2 = internalEnd.x
        y2 = internalEnd.y

        xy = [x1, y1, x2, y2]

        return xy

    def __toInternal(self, position: Position) -> InternalPosition:

        verticalGap:   int = self._diagramPadding.verticalGap
        horizontalGap: int = self._diagramPadding.horizontalGap

        iPos: InternalPosition = ImageCommon.toInternal(position, verticalGap=verticalGap, horizontalGap=horizontalGap)

        return iPos
