
from logging import Logger
from logging import getLogger
from typing import cast

from unittest import TestSuite
from unittest import main as unitTestMain

from pdfdiagrams.Definitions import ArrowAttachmentSide
from pdfdiagrams.Definitions import ClassDefinition
from pdfdiagrams.Definitions import ClassDefinitions
from pdfdiagrams.Definitions import DefinitionType
from pdfdiagrams.Definitions import LineDefinition
from pdfdiagrams.Definitions import LineDefinitions
from pdfdiagrams.Definitions import LineType
from pdfdiagrams.Definitions import MethodDefinition
from pdfdiagrams.Definitions import ParameterDefinition
from pdfdiagrams.Definitions import Position
from pdfdiagrams.Definitions import Size

from pdfdiagrams.Diagram import Diagram
from pdfdiagrams.DiagramCommon import DiagramCommon
from pdfdiagrams.DiagramLine import DiagramLine

from tests.TestBase import TestBase


class TestDiagram(TestBase):
    """
    The following all test with the default horizontal/vertical gaps and the default top/left margins

    """

    TEST_SUFFIX:          str = f'.pdf'
    TEST_FILE_NAME:       str = 'Test'
    BASE_TEST_CLASS_NAME: str = 'TestClassName'

    TEST_LAST_X_POSITION: int = 9
    TEST_LAST_Y_POSITION: int = 6

    TEST_DPI: int = 72

    clsLogger: Logger = None

    @classmethod
    def setUpClass(cls):
        TestBase.setUpLogging()
        TestDiagram.clsLogger = getLogger(__name__)

    def setUp(self):
        self.logger: Logger = TestDiagram.clsLogger

    def tearDown(self):
        pass

    def testConstruction(self):

        diagram: Diagram = Diagram(fileName=TestDiagram.TEST_FILE_NAME, dpi=TestDiagram.TEST_DPI)
        self.assertIsNotNone(diagram, 'Construction failed')

        self.assertEqual(Diagram.DEFAULT_FONT_SIZE, diagram.fontSize, 'Default font size changed')

    def testBasicDiagramDraw(self):

        diagram: Diagram = Diagram(fileName=f'{TestDiagram.TEST_FILE_NAME}-Basic{TestDiagram.TEST_SUFFIX}', dpi=TestDiagram.TEST_DPI)
        classDef: ClassDefinition = ClassDefinition(name=TestDiagram.BASE_TEST_CLASS_NAME,
                                                    size=Size(width=Diagram.DEFAULT_CELL_WIDTH, height=Diagram.DEFAULT_CELL_HEIGHT))

        diagram.drawClass(classDef)
        diagram.write()

    def testFillPage(self):

        diagram: Diagram = Diagram(fileName=f'{TestDiagram.TEST_FILE_NAME}-Full{TestDiagram.TEST_SUFFIX}', dpi=TestDiagram.TEST_DPI)

        widthInterval:  int = Diagram.DEFAULT_CELL_WIDTH // 10
        heightInterval: int = Diagram.DEFAULT_CELL_HEIGHT // 10

        for x in range(0, TestDiagram.TEST_LAST_X_POSITION):
            scrX: int = (x * Diagram.DEFAULT_CELL_WIDTH) + (widthInterval * x)

            for y in range(0, TestDiagram.TEST_LAST_Y_POSITION):

                scrY: int = (y * Diagram.DEFAULT_CELL_HEIGHT) + (y * heightInterval)
                classDef: ClassDefinition = ClassDefinition(name=f'{TestDiagram.BASE_TEST_CLASS_NAME}{x}{y}',
                                                            position=Position(scrX, scrY),
                                                            size=Size(width=Diagram.DEFAULT_CELL_WIDTH, height=Diagram.DEFAULT_CELL_HEIGHT))
                diagram.drawClass(classDef)

        diagram.write()

    def testBasicMethods(self):

        diagram: Diagram = Diagram(fileName=f'{TestDiagram.TEST_FILE_NAME}-BasicMethods{TestDiagram.TEST_SUFFIX}', dpi=TestDiagram.TEST_DPI)

        classDef: ClassDefinition = self.__buildCar()

        diagram.drawClass(classDef)

        diagram.write()

    def testSophisticatedLayout(self):

        diagram: Diagram = Diagram(fileName=f'{TestDiagram.TEST_FILE_NAME}-SophisticatedLayout{TestDiagram.TEST_SUFFIX}', dpi=TestDiagram.TEST_DPI)

        classDefinitions: ClassDefinitions = [
            self.__buildCar(),
            self.__buildCat(),
            self.__buildOpie(),
            self.__buildNameTestCase(),
            self.__buildElectricCar()
        ]
        for classDefinition in classDefinitions:
            classDefinition = cast(ClassDefinition, classDefinition)
            diagram.drawClass(classDefinition=classDefinition)

        lineDefinitions: LineDefinitions = self.__buildSophisticatedLineDefinitions()
        for lineDefinition in lineDefinitions:
            diagram.drawLine(lineDefinition=lineDefinition)

        diagram.write()

    V_LEFT_X:   int = 1100
    V_RIGHT_X:  int = 1250
    V_TOP_Y:    int = 394
    V_BOTTOM_Y: int = 508

    X_INC: int = 50
    X_DEC: int = 50

    TOP_LINE_LEFT_X:  int = V_LEFT_X  - X_DEC
    TOP_LINE_RIGHT_X: int = V_RIGHT_X + X_INC

    H_LEFT_X:        int = V_RIGHT_X + 300
    H_RIGHT_X:       int = H_LEFT_X  + 200
    H_LEFT_TOP_Y:    int = V_TOP_Y
    H_LEFT_BOTTOM_Y: int = V_BOTTOM_Y

    Y_INC: int = 50
    DASH_LINE_SPACE_LENGTH: int = 4

    def testLineDraws(self):
        diagram: Diagram = Diagram(fileName=f'{TestDiagram.TEST_FILE_NAME}-LineDraws{TestDiagram.TEST_SUFFIX}', dpi=TestDiagram.TEST_DPI)

        self.__drawHorizontalBoundaries(diagram)
        self.__drawVerticalBoundaries(diagram)

        lineDrawer: DiagramLine = DiagramLine(pdf=diagram._pdf, diagramPadding=diagram._diagramPadding, dpi=diagram._dpi)

        lineDefinitions: LineDefinitions = [
            self.__buildSouthAttachedInheritanceDefinition(),
            self.__buildNorthAttachedInheritanceDefinition(),
            self.__buildEastAttachedInheritanceDefinition()
        ]
        for lineDefinition in lineDefinitions:

            lineDrawer.draw(lineDefinition)

        diagram.write()

    def testBuildMethod(self):

        diagram: Diagram = Diagram(fileName=cast(str, None), dpi=cast(int, None))

        initMethodDef: MethodDefinition = self.__buildInitMethod()

        actualRepr:    str = diagram._buildMethod(initMethodDef)
        expectedRepr:  str = '+ __init__(make: str, model: str, year: int=1957)'

        self.assertEqual(expectedRepr, actualRepr, 'Method building is incorrect')

    def testBuildMethods(self):

        diagram: Diagram = Diagram(fileName=cast(str, None), dpi=cast(int, None))

        car: ClassDefinition = self.__buildCar()

        reprs: Diagram.MethodsRepr = diagram._buildMethods(car.methods)

        self.assertEqual(5, len(reprs), 'Generated incorrect number of method representations')

    def __buildCar(self) -> ClassDefinition:

        car: ClassDefinition = ClassDefinition(name='car', position=Position(107, 30), size=Size(width=266, height=100))

        initMethodDef:      MethodDefinition = self.__buildInitMethod()
        descMethodDef:      MethodDefinition = MethodDefinition(name='getDescriptiveName', visibility=DefinitionType.Public)
        odometerMethodDef:  MethodDefinition = MethodDefinition(name='readOdometer',      visibility=DefinitionType.Public)
        updateOdoMethodDef: MethodDefinition = MethodDefinition(name='updateOdometer',    visibility=DefinitionType.Public)
        incrementMethodDef: MethodDefinition = MethodDefinition(name='incrementOdometer', visibility=DefinitionType.Protected)

        mileageParam: ParameterDefinition = ParameterDefinition(name='mileage', defaultValue='1')
        updateOdoMethodDef.parameters = [mileageParam]

        milesParam: ParameterDefinition = ParameterDefinition(name='miles', parameterType='int')
        incrementMethodDef.parameters = [milesParam]

        car.methods = [initMethodDef, descMethodDef, odometerMethodDef, updateOdoMethodDef, incrementMethodDef]

        return car

    def __buildCat(self) -> ClassDefinition:

        cat: ClassDefinition = ClassDefinition(name='gato', position=Position(536, 19), size=Size(height=74, width=113))

        initMethod:     MethodDefinition = MethodDefinition('__init')
        sitMethod:      MethodDefinition = MethodDefinition('sit')
        rollOverMethod: MethodDefinition = MethodDefinition('rollOver')

        cat.methods = [initMethod, sitMethod, rollOverMethod]

        return cat

    def __buildOpie(self) -> ClassDefinition:

        opie: ClassDefinition = ClassDefinition(name='Opie', position=Position(495, 208), size=Size(width=216, height=87))

        publicMethod: MethodDefinition = MethodDefinition(name='publicMethod', visibility=DefinitionType.Public, returnType='bool')
        paramDef: ParameterDefinition  = ParameterDefinition(name='param', parameterType='float', defaultValue='23.0')

        publicMethod.parameters = [paramDef]

        opie.methods = [publicMethod]

        return opie

    def __buildElectricCar(self) -> ClassDefinition:

        electricCar: ClassDefinition = ClassDefinition(name='ElectricCar', position=Position(52, 224), size=Size(width=173, height=64))

        initMethod: MethodDefinition = MethodDefinition(name='__init__')
        descMethod: MethodDefinition = MethodDefinition(name='describeBattery')

        makeParameter:  ParameterDefinition = ParameterDefinition(name='make')
        modelParameter: ParameterDefinition = ParameterDefinition(name='model')
        yearParameter:  ParameterDefinition = ParameterDefinition(name='year')

        initMethod.parameters = [makeParameter, modelParameter, yearParameter]
        electricCar.methods = [initMethod, descMethod]
        return electricCar

    def __buildNameTestCase(self) -> ClassDefinition:

        namesTest: ClassDefinition = ClassDefinition(name='NamesTestCase', position=Position(409, 362), size=Size(height=65, width=184))

        testFirst:    MethodDefinition = MethodDefinition(name='testFirstLasName')
        formattedName: MethodDefinition = MethodDefinition(name='getFormattedName')

        firstParam:  ParameterDefinition = ParameterDefinition(name='first')
        lastParam:  ParameterDefinition = ParameterDefinition(name='last')

        formattedName.parameters = [firstParam, lastParam]
        namesTest.methods = [testFirst, formattedName]

        return namesTest

    def __buildInitMethod(self) -> MethodDefinition:

        initMethodDef:  MethodDefinition    = MethodDefinition(name='__init__', visibility=DefinitionType.Public)

        initParam:  ParameterDefinition = ParameterDefinition(name='make',  parameterType='str', defaultValue='')
        modelParam: ParameterDefinition = ParameterDefinition(name='model', parameterType='str', defaultValue='')
        yearParam:  ParameterDefinition = ParameterDefinition(name='year',  parameterType='int', defaultValue='1957')

        initMethodDef.parameters = [initParam, modelParam, yearParam]

        return initMethodDef

    def __buildSophisticatedLineDefinitions(self) -> LineDefinitions:

        lineDefinitions: LineDefinitions = [
            self.__buildSouthAttachedInheritanceDefinition()
        ]

        return lineDefinitions

    def __buildSouthAttachedInheritanceDefinition(self) -> LineDefinition:
        return LineDefinition(lineType=LineType.Inheritance, arrowAttachmentSide=ArrowAttachmentSide.SOUTH,
                              source=Position(TestDiagram.V_LEFT_X, TestDiagram.V_BOTTOM_Y), destination=Position(TestDiagram.V_LEFT_X, TestDiagram.V_TOP_Y))

    def __buildNorthAttachedInheritanceDefinition(self) -> LineDefinition:
        return LineDefinition(lineType=LineType.Inheritance, arrowAttachmentSide=ArrowAttachmentSide.NORTH,
                              destination=Position(TestDiagram.V_RIGHT_X, TestDiagram.V_BOTTOM_Y), source=Position(TestDiagram.V_RIGHT_X, TestDiagram.V_TOP_Y))

    def __buildEastAttachedInheritanceDefinition(self) -> LineDefinition:

        yTop: int = TestDiagram.H_LEFT_TOP_Y + TestDiagram.Y_INC
        return LineDefinition(lineType=LineType.Inheritance,
                              arrowAttachmentSide=ArrowAttachmentSide.EAST,
                              source=Position(TestDiagram.H_LEFT_X, yTop),
                              destination=Position(TestDiagram.H_RIGHT_X, yTop)
                              )

    def __drawHorizontalBoundaries(self, diagram: Diagram):

        x1: int = DiagramCommon.toPdfPoints(TestDiagram.TOP_LINE_LEFT_X,  diagram._dpi) + DiagramCommon.LEFT_MARGIN + diagram.verticalGap
        x2: int = DiagramCommon.toPdfPoints(TestDiagram.TOP_LINE_RIGHT_X, diagram._dpi) + DiagramCommon.LEFT_MARGIN + diagram.verticalGap
        y2: int = DiagramCommon.toPdfPoints(TestDiagram.V_BOTTOM_Y,       diagram._dpi) + DiagramCommon.TOP_MARGIN  + diagram.verticalGap

        diagram._pdf.dashed_line(x1=x1, y1=y2, x2=x2, y2=y2, space_length=TestDiagram.DASH_LINE_SPACE_LENGTH)

        y2 = DiagramCommon.toPdfPoints(TestDiagram.V_TOP_Y, diagram._dpi) + DiagramCommon.TOP_MARGIN + diagram.verticalGap

        diagram._pdf.dashed_line(x1=x1, y1=y2, x2=x2, y2=y2, space_length=TestDiagram.DASH_LINE_SPACE_LENGTH)

    def __drawVerticalBoundaries(self, diagram: Diagram):

        x1: int = DiagramCommon.toPdfPoints(TestDiagram.H_LEFT_X,  diagram._dpi) + DiagramCommon.LEFT_MARGIN + diagram.verticalGap
        x2: int = x1
        y1: int = DiagramCommon.toPdfPoints(TestDiagram.H_LEFT_TOP_Y,    diagram._dpi) + DiagramCommon.LEFT_MARGIN + diagram.verticalGap
        y2: int = DiagramCommon.toPdfPoints(TestDiagram.H_LEFT_BOTTOM_Y, diagram._dpi) + DiagramCommon.LEFT_MARGIN + diagram.verticalGap

        diagram._pdf.dashed_line(x1=x1, y1=y1, x2=x2, y2=y2, space_length=TestDiagram.DASH_LINE_SPACE_LENGTH)

        x1 = DiagramCommon.toPdfPoints(TestDiagram.H_RIGHT_X,  diagram._dpi) + DiagramCommon.LEFT_MARGIN + diagram.verticalGap
        x2 = x1

        diagram._pdf.dashed_line(x1=x1, y1=y1, x2=x2, y2=y2, space_length=TestDiagram.DASH_LINE_SPACE_LENGTH)


def suite() -> TestSuite:
    """You need to change the name of the test class here also."""
    import unittest

    testSuite: TestSuite = TestSuite()
    # noinspection PyUnresolvedReferences
    testSuite.addTest(unittest.makeSuite(TestDiagram))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
