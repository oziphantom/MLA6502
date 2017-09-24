from unittest import TestCase
from assemNumHelper import AssemNumHelper


class TestAssemNumHelper(TestCase):
    def test_is_immediate(self):
        self.assertTrue(AssemNumHelper.is_immediate("#1"))
        self.assertTrue(AssemNumHelper.is_immediate("#$50"))
        self.assertTrue(AssemNumHelper.is_immediate("#%1011"))
        self.assertTrue(AssemNumHelper.is_immediate("\t  \t  \t#1"))
        self.assertTrue(AssemNumHelper.is_immediate("  #1"))
        self.assertFalse(AssemNumHelper.is_immediate("1"))
        self.assertFalse(AssemNumHelper.is_immediate("$50"))
        self.assertFalse(AssemNumHelper.is_immediate("%1011"))
        self.assertFalse(AssemNumHelper.is_immediate("\t  \t  \t1"))
        self.assertFalse(AssemNumHelper.is_immediate("  1"))
        self.assertFalse(AssemNumHelper.is_immediate("test"))
        self.assertFalse(AssemNumHelper.is_immediate("test.otherTest"))
        self.assertFalse(AssemNumHelper.is_immediate("kMything"))
        self.assertTrue(AssemNumHelper.is_immediate("#test"))
        self.assertTrue(AssemNumHelper.is_immediate("#kTest.test"))

    def test_is_binary(self):
        self.assertFalse(AssemNumHelper.is_binary("#1"))
        self.assertFalse(AssemNumHelper.is_binary("#$50"))
        self.assertTrue(AssemNumHelper.is_binary("#%1011"))
        self.assertFalse(AssemNumHelper.is_binary("\t  \t  \t#1"))
        self.assertFalse(AssemNumHelper.is_binary("  #1"))
        self.assertFalse(AssemNumHelper.is_binary("1"))
        self.assertFalse(AssemNumHelper.is_binary("$50"))
        self.assertTrue(AssemNumHelper.is_binary("%1011"))
        self.assertFalse(AssemNumHelper.is_binary("\t  \t  \t1"))
        self.assertFalse(AssemNumHelper.is_binary("  1"))
        self.assertFalse(AssemNumHelper.is_binary("test"))
        self.assertFalse(AssemNumHelper.is_binary("test.otherTest"))
        self.assertFalse(AssemNumHelper.is_binary("kMything"))
        self.assertFalse(AssemNumHelper.is_binary("#test"))
        self.assertFalse(AssemNumHelper.is_binary("#kTest.test"))

    def test_is_hex(self):
        self.assertFalse(AssemNumHelper.is_hex("#1"))
        self.assertTrue(AssemNumHelper.is_hex("#$50"))
        self.assertFalse(AssemNumHelper.is_hex("#%1011"))
        self.assertFalse(AssemNumHelper.is_hex("\t  \t  \t#1"))
        self.assertFalse(AssemNumHelper.is_hex("  #1"))
        self.assertFalse(AssemNumHelper.is_hex("1"))
        self.assertTrue(AssemNumHelper.is_hex("$50"))
        self.assertFalse(AssemNumHelper.is_hex("%1011"))
        self.assertFalse(AssemNumHelper.is_hex("\t  \t  \t1"))
        self.assertFalse(AssemNumHelper.is_hex("  1"))
        self.assertFalse(AssemNumHelper.is_hex("test"))
        self.assertFalse(AssemNumHelper.is_hex("test.otherTest"))
        self.assertFalse(AssemNumHelper.is_hex("kMything"))
        self.assertFalse(AssemNumHelper.is_hex("#test"))
        self.assertFalse(AssemNumHelper.is_hex("#kTest.test"))

    def test_get_int_from_hex(self):
        self.assertEqual(AssemNumHelper.get_int_from_hex("$01"), 1)
        self.assertEqual(AssemNumHelper.get_int_from_hex("$0f"), 15)
        self.assertEqual(AssemNumHelper.get_int_from_hex("$A0"), 160)
        self.assertEqual(AssemNumHelper.get_int_from_hex("$4000"), 0x4000)
        with self.assertRaises(ValueError):
            AssemNumHelper.get_int_from_hex("4000")
        with self.assertRaises(ValueError):
            AssemNumHelper.get_int_from_hex("#$01")
        with self.assertRaises(ValueError):
            AssemNumHelper.get_int_from_hex("%1101")

    def test_get_int_from_binary(self):
        self.assertEqual(AssemNumHelper.get_int_from_binary("%1101"), 13)
        self.assertEqual(AssemNumHelper.get_int_from_binary("%10000000"), 128)
        self.assertEqual(AssemNumHelper.get_int_from_binary("%111010110111100110100010101"), 123456789)
        with self.assertRaises(ValueError):
            AssemNumHelper.get_int_from_binary("4000")
        with self.assertRaises(ValueError):
            AssemNumHelper.get_int_from_binary("#$01")
        with self.assertRaises(ValueError):
            AssemNumHelper.get_int_from_binary("1101")

    def test_is_equation(self):
        self.assertTrue(AssemNumHelper.is_equation("1 + 2"))
        self.assertTrue(AssemNumHelper.is_equation("1 * 2"))
        self.assertTrue(AssemNumHelper.is_equation("1 - 2"))
        self.assertTrue(AssemNumHelper.is_equation("1 / 2"))
        self.assertTrue(AssemNumHelper.is_equation("kSprite + 5*8"))
        self.assertFalse(AssemNumHelper.is_equation("1"))
        self.assertFalse(AssemNumHelper.is_equation("#1"))
        self.assertFalse(AssemNumHelper.is_equation("$1"))
        self.assertFalse(AssemNumHelper.is_equation("kSprite"))

    def test_convert_equation_to_python(self):
        self.assertEqual(AssemNumHelper.convert_equation_to_python("1 + 2"), "1 + 2")
        self.assertEqual(AssemNumHelper.convert_equation_to_python("$1 + 2"), "0x1 + 2")
        self.assertEqual(AssemNumHelper.convert_equation_to_python("$1 + $2"), "0x1 + 0x2")
        self.assertEqual(AssemNumHelper.convert_equation_to_python("%101 + kSprNum"), "0b101 + kSprNum")
        self.assertEqual(AssemNumHelper.convert_equation_to_python("%101 + kSprNum * %01"), "0b101 + kSprNum * 0b01")
        self.assertEqual(AssemNumHelper.convert_equation_to_python("kVectors.screen.basePtr"), "kVectors_screen_basePtr")

    def test_get_invalid_value(self):
        self.assertGreaterEqual(AssemNumHelper.get_invalid_value(), 0x10000)

    def test_is_invalid_value(self):
        self.assertFalse(AssemNumHelper.is_invalid_value(0))
        self.assertFalse(AssemNumHelper.is_invalid_value(100))
        self.assertFalse(AssemNumHelper.is_invalid_value(256))
        self.assertFalse(AssemNumHelper.is_invalid_value(4096))
        self.assertFalse(AssemNumHelper.is_invalid_value(0xfff))
        self.assertTrue(AssemNumHelper.is_invalid_value(0x10000))
        self.assertTrue(AssemNumHelper.is_invalid_value(AssemNumHelper.get_invalid_value()))

    def test_is_number_negative(self):
        self.assertFalse(AssemNumHelper.is_number_negative(0))
        self.assertFalse(AssemNumHelper.is_number_negative(1))
        self.assertFalse(AssemNumHelper.is_number_negative(32))
        self.assertFalse(AssemNumHelper.is_number_negative(64))
        self.assertFalse(AssemNumHelper.is_number_negative(127))
        self.assertTrue(AssemNumHelper.is_number_negative(128))
        self.assertTrue(AssemNumHelper.is_number_negative(192))
        self.assertTrue(AssemNumHelper.is_number_negative(255))

    def test_is_number_positive(self):
        self.assertTrue(AssemNumHelper.is_number_positive(0))
        self.assertTrue(AssemNumHelper.is_number_positive(1))
        self.assertTrue(AssemNumHelper.is_number_positive(32))
        self.assertTrue(AssemNumHelper.is_number_positive(64))
        self.assertTrue(AssemNumHelper.is_number_positive(127))
        self.assertFalse(AssemNumHelper.is_number_positive(128))
        self.assertFalse(AssemNumHelper.is_number_positive(192))
        self.assertFalse(AssemNumHelper.is_number_positive(255))
