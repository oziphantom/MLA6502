from unittest import TestCase
from tassLineGroup import TassLineGroupType
from tassLineGroup import TassLineGroup

class TestTassLineGroup(TestCase):
    def test_should_evaluate_if(self):
        under_test = TassLineGroup()
        under_test.type = TassLineGroupType.not_special
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.weak
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.if_block
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.block
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.comment
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.struct
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.section
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.union
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.include
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.binary
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.midlevel
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.root
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.end_if
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.end_block
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.end_comment
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.end_struct
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.end_macro
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.end_union
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.end_section
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.end_function
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.end_weak
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.preprocessor_assign
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.assign
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.if_else
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.just_else
        self.assertTrue(TassLineGroup.should_evaluate_if(under_test))

        under_test.type = TassLineGroupType.macro
        self.assertFalse(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.segment
        self.assertFalse(TassLineGroup.should_evaluate_if(under_test))
        under_test.type = TassLineGroupType.function
        self.assertFalse(TassLineGroup.should_evaluate_if(under_test))

    def test_type_allows_runs(self):
        self.assertTrue(TassLineGroup.type_allows_runs(TassLineGroupType.not_special))
        self.assertTrue(TassLineGroup.type_allows_runs(TassLineGroupType.weak))
        self.assertFalse(TassLineGroup.type_allows_runs(TassLineGroupType.if_block))
        self.assertFalse(TassLineGroup.type_allows_runs(TassLineGroupType.block))
        self.assertTrue(TassLineGroup.type_allows_runs(TassLineGroupType.comment))
        self.assertFalse(TassLineGroup.type_allows_runs(TassLineGroupType.struct))
        self.assertFalse(TassLineGroup.type_allows_runs(TassLineGroupType.section))
        self.assertTrue(TassLineGroup.type_allows_runs(TassLineGroupType.macro))
        self.assertTrue(TassLineGroup.type_allows_runs(TassLineGroupType.segment))
        self.assertTrue(TassLineGroup.type_allows_runs(TassLineGroupType.union))
        self.assertFalse(TassLineGroup.type_allows_runs(TassLineGroupType.include))
        self.assertFalse(TassLineGroup.type_allows_runs(TassLineGroupType.binary))
        self.assertTrue(TassLineGroup.type_allows_runs(TassLineGroupType.midlevel))
        self.assertTrue(TassLineGroup.type_allows_runs(TassLineGroupType.root))
        self.assertFalse(TassLineGroup.type_allows_runs(TassLineGroupType.end_if))
        self.assertFalse(TassLineGroup.type_allows_runs(TassLineGroupType.end_block))
        self.assertFalse(TassLineGroup.type_allows_runs(TassLineGroupType.end_comment))
        self.assertFalse(TassLineGroup.type_allows_runs(TassLineGroupType.end_struct))
        self.assertFalse(TassLineGroup.type_allows_runs(TassLineGroupType.end_macro))
        self.assertTrue(TassLineGroup.type_allows_runs(TassLineGroupType.end_union))
        self.assertFalse(TassLineGroup.type_allows_runs(TassLineGroupType.end_section))
        self.assertTrue(TassLineGroup.type_allows_runs(TassLineGroupType.end_weak))
        self.assertTrue(TassLineGroup.type_allows_runs(TassLineGroupType.preprocessor_assign))
        self.assertTrue(TassLineGroup.type_allows_runs(TassLineGroupType.assign))
        self.assertTrue(TassLineGroup.type_allows_runs(TassLineGroupType.if_else))
        self.assertTrue(TassLineGroup.type_allows_runs(TassLineGroupType.just_else))
        self.assertTrue(TassLineGroup.type_allows_runs(TassLineGroupType.function))
        self.assertTrue(TassLineGroup.type_allows_runs(TassLineGroupType.end_function))


    def test_get_end_type_for_type(self):
        self.fail()

    def test_get_does_type_make_sub_blocks(self):
        self.fail()

    def test_identify_line(self):
        self.fail()
