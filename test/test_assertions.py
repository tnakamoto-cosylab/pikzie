import os
import re
import shutil
import syslog
import pikzie
import test.utils

base_path = os.path.dirname(__file__)
tmp_path = os.path.join(base_path, "tmp")
nonexistent_path = os.path.join(base_path, "nonexistent")

class TestAssertions(pikzie.TestCase, test.utils.Assertions):
    """Tests for assertions."""

    class TestCase(pikzie.TestCase):
        def setup(self):
            shutil.rmtree(tmp_path, True)
            shutil.rmtree(nonexistent_path, True)

        def test_fail(self):
            self.fail("Failed!!!")

        def test_pend(self):
            self.assert_equal(3, 1 + 2)
            self.pend("Pending!!!")
            self.assert_equal(5, 3 + 2)

        def test_notify(self):
            self.assert_equal(3, 1 + 2)
            self.notify("Notification!!!")
            self.assert_equal(5, 3 + 2)

        def test_assert_none(self):
            self.assert_none(None)
            self.assert_none(False)

        def test_assert_not_none(self):
            self.assert_not_none(False)
            self.assert_not_none(None)

        def test_assert_true_for_none(self):
            self.assert_true(None)

        def test_assert_true_for_boolean(self):
            self.assert_true(True)
            self.assert_true(False)
            self.assert_true(True)

        def test_assert_true_for_integer(self):
            self.assert_true(10)
            self.assert_true(0)
            self.assert_true(-100)

        def test_assert_true_for_string(self):
            self.assert_true("String")
            self.assert_true("")
            self.assert_true("STRING")

        def test_assert_false_for_none(self):
            self.assert_false(None)

        def test_assert_false_for_boolean(self):
            self.assert_false(False)
            self.assert_false(True)
            self.assert_false(False)

        def test_assert_false_for_integer(self):
            self.assert_false(0)
            self.assert_false(10)
            self.assert_false(0)

        def test_assert_false_for_string(self):
            self.assert_false("")
            self.assert_false("STRING")
            self.assert_false("")

        def test_assert_equal(self):
            self.assert_equal(1, 1)
            self.assert_equal(2, 3)
            self.assert_equal(5, 5)

        def test_assert_not_equal(self):
            self.assert_not_equal(2, 3)
            self.assert_not_equal(2, 2)
            self.assert_not_equal(5, 1)

        def test_assert_not_equal_different_repr(self):
            class AlwaysEqual(object):
                def __init__(self, repr):
                    self.repr = repr

                def __ne__(self, other):
                    return False

                def __repr__(self):
                    return repr(self.repr)

            self.assert_not_equal(AlwaysEqual("abc"), AlwaysEqual("aBc"))

        def test_assert_in_delta(self):
            self.assert_in_delta(0.5, 0.5001, 0.01)
            self.assert_in_delta(0.5, 0.5001, 0.001)
            self.assert_in_delta(0.5, 0.5001, 0.0001)
            self.assert_in_delta(0.5, 0.5001, 0.00001)
            self.assert_in_delta(0.5, 0.5001, 0.000001)

        def test_assert_match(self):
            self.assert_match("abc", "abcde")
            self.assert_match("abc", "Xabcde")

        def test_assert_match_re(self):
            self.assert_match(re.compile("xyz"), "xyzabc")
            self.assert_match(re.compile("xyz"), "abcxyz")

        def test_assert_not_match(self):
            self.assert_not_match("abc", "Xabcde")
            self.assert_not_match("abc", "abcde")

        def test_assert_not_match_re(self):
            self.assert_not_match(re.compile("xyz", re.I), "abcXYZ")
            self.assert_not_match(re.compile("xyz", re.I), "XYZabc")

        def test_assert_search(self):
            self.assert_search("bcd", "abcde")
            self.assert_search("bcd", "bcd")
            self.assert_search("bcd", "abCde")

        def test_assert_search_re(self):
            self.assert_search(re.compile("xyz"), "AxyzA")
            self.assert_search(re.compile("xyz"), "xyz")
            self.assert_search(re.compile("xyz"), "AxYzA")

        def test_assert_not_found(self):
            self.assert_not_found("bcd", "abCde")
            self.assert_not_found(re.compile("bcd"), "abCde")
            self.assert_not_found(re.compile("bcd", re.I | re.L), "abCde")

        def test_assert_hasattr(self):
            self.assert_hasattr("string", "ljust")
            self.assert_hasattr("string", "strip")
            self.assert_hasattr("string", "Strip")
            self.assert_hasattr("string", "index")

        def test_assert_callable(self):
            class Callable(object):
                def __call__(self):
                    return "X"

            self.assert_callable(Callable())
            self.assert_callable(lambda : "zzz")
            self.assert_callable("string")
            self.assert_callable(self.test_assert_callable)

        def test_assert_call_raise(self):
            def raise_name_error():
                unknown_name
            exception = self.assert_call_raise(NameError, raise_name_error)
            self.assert_equal("global name \'unknown_name\' is not defined",
                              str(exception))

            def nothing_raised():
                "nothing raised"
            self.assert_call_raise(NameError, nothing_raised)

        def test_assert_call_raise_different_error(self):
            def raise_zero_division_error():
                1 / 0
            self.assert_call_raise(NameError, raise_zero_division_error)

        def test_assert_call_nothing_raised(self):
            self.assert_equal(123, self.assert_call_nothing_raised(lambda : 123))
            def raise_zero_division_error():
                1 / 0
            self.assert_call_nothing_raised(raise_zero_division_error)

        def test_assert_run_command(self):
            process = self.assert_run_command(["echo", "12345"])
            self.assert_equal("12345\n", process.stdout.read())
            self.assert_run_command("false")

        def test_assert_run_command_unknown(self):
            self.assert_run_command(["unknown", "arg1", "arg2"])

        def test_assert_search_syslog_in_calling(self):
            self.assert_search_syslog_in_calling("find me!+",
                                                 syslog.syslog, "find me!!!")
            self.assert_search_syslog_in_calling("fix me!",
                                                 syslog.syslog, "FIXME!!!")

        def test_assert_open_file(self):
            file = self.assert_open_file(__file__)
            self.assert_equal("r", file.mode)
            file = self.assert_open_file(tmp_path, "w")
            self.assert_equal("w", file.mode)
            self.assert_open_file(nonexistent_path)

    def test_fail(self):
        """Test for fail"""
        self.assert_result(False, 1, 0, 1, 0, 0, 0,
                           [("F", "TestCase.test_fail", "Failed!!!", None)],
                           ["test_fail"])

    def test_pend(self):
        self.assert_result(True, 1, 1, 0, 0, 1, 0,
                           [('P',
                             "TestCase.test_pend",
                             "Pending!!!",
                             None)],
                           ["test_pend"])

    def test_notify(self):
        self.assert_result(True, 1, 2, 0, 0, 0, 1,
                           [('N',
                             "TestCase.test_notify",
                             "Notification!!!",
                             None)],
                           ["test_notify"])

    def test_assert_none(self):
        self.assert_result(False, 1, 1, 1, 0, 0, 0,
                           [("F",
                             "TestCase.test_assert_none",
                             "expected: <False> is None",
                             None)],
                           ["test_assert_none"])

    def test_assert_not_none(self):
        self.assert_result(False, 1, 1, 1, 0, 0, 0,
                           [("F",
                             "TestCase.test_assert_not_none",
                             "expected: not None",
                             None)],
                           ["test_assert_not_none"])

    def test_assert_true(self):
        self.assert_result(False, 4, 3, 4, 0, 0, 0,
                           [("F",
                             "TestCase.test_assert_true_for_none",
                             "expected: <None> is a true value",
                             None),
                            ("F",
                             "TestCase.test_assert_true_for_boolean",
                             "expected: <False> is a true value",
                             None),
                            ("F",
                             "TestCase.test_assert_true_for_integer",
                             "expected: <0> is a true value",
                             None),
                            ("F",
                             "TestCase.test_assert_true_for_string",
                             "expected: <''> is a true value",
                             None)],
                           ["test_assert_true_for_none",
                            "test_assert_true_for_boolean",
                            "test_assert_true_for_integer",
                            "test_assert_true_for_string"])

    def test_assert_false(self):
        self.assert_result(False, 4, 4, 3, 0, 0, 0,
                           [("F",
                             "TestCase.test_assert_false_for_boolean",
                             "expected: <True> is a false value",
                             None),
                            ("F",
                             "TestCase.test_assert_false_for_integer",
                             "expected: <10> is a false value",
                             None),
                            ("F",
                             "TestCase.test_assert_false_for_string",
                             "expected: <'STRING'> is a false value",
                             None)],
                           ["test_assert_false_for_none",
                            "test_assert_false_for_boolean",
                            "test_assert_false_for_integer",
                            "test_assert_false_for_string"])

    def test_assert_equal(self):
        self.assert_result(False, 1, 1, 1, 0, 0, 0,
                           [('F',
                             'TestCase.test_assert_equal',
                             "expected: <2>\n"
                             " but was: <3>\n"
                             "diff:\n"
                             "- 2\n"
                             "+ 3",
                             None)],
                           ["test_assert_equal"])

    def test_assert_not_equal(self):
        self.assert_result(False, 2, 1, 2, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_not_equal",
                             "not expected: <2>\n"
                             "     but was: <2>",
                             None),
                            ("F",
                             "TestCase.test_assert_not_equal_different_repr",
                             "not expected: <'abc'>\n"
                             "     but was: <'aBc'>\n"
                             "diff:\n"
                             "- 'abc'\n"
                             "?   ^\n"
                             "\n"
                             "+ 'aBc'\n"
                             "?   ^\n",
                             None)],
                           ["test_assert_not_equal",
                            "test_assert_not_equal_different_repr"])

    def test_assert_in_delta(self):
        expected = 0.5
        actual = 0.5001
        delta = 0.00001
        params = (expected, delta, [expected - delta, expected + delta], actual)
        self.assert_result(False, 1, 3, 1, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_in_delta",
                             "expected: <%r+-%r %r>\n"
                             " but was: <%r>" % params,
                             None)],
                           ["test_assert_in_delta"])

    def test_assert_match(self):
        self.assert_result(False, 2, 2, 2, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_match",
                             "expected: re.match('abc', 'Xabcde') "
                               "doesn't return None\n"
                             " pattern: </abc/>\n"
                             "  target: <'Xabcde'>",
                             None),
                            ('F',
                             "TestCase.test_assert_match_re",
                             "expected: re.match('xyz', 'abcxyz') "
                               "doesn't return None\n"
                             " pattern: </xyz/>\n"
                             "  target: <'abcxyz'>",
                             None)],
                           ["test_assert_match",
                            "test_assert_match_re"])

    def test_assert_not_match(self):
        self.assert_result(False, 2, 2, 2, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_not_match",
                             "expected: re.match('abc', 'abcde') returns None\n"
                             " pattern: </abc/>\n"
                             "  target: <'abcde'>",
                             None),
                            ('F',
                             "TestCase.test_assert_not_match_re",
                             "expected: re.match(%s, 'XYZabc') returns None\n"
                             " pattern: </xyz/i>\n"
                             "  target: <'XYZabc'>" % \
                                 ("re.compile('xyz', re.IGNORECASE)"),
                             None)],
                           ["test_assert_not_match",
                            "test_assert_not_match_re"])

    def test_assert_search(self):
        self.assert_result(False, 2, 4, 2, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_search",
                             "expected: re.search('bcd', 'abCde') "
                               "doesn't return None\n"
                             " pattern: </bcd/>\n"
                             "  target: <'abCde'>",
                             None),
                            ('F',
                             "TestCase.test_assert_search_re",
                             "expected: re.search('xyz', 'AxYzA') "
                               "doesn't return None\n"
                             " pattern: </xyz/>\n"
                             "  target: <'AxYzA'>",
                             None)],
                           ["test_assert_search",
                            "test_assert_search_re"])

    def test_assert_not_found(self):
        re_repr = "re.compile('bcd', re.IGNORECASE | re.LOCALE)"
        self.assert_result(False, 1, 2, 1, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_not_found",
                             "expected: re.search(%s, 'abCde') returns None\n"
                             " pattern: </bcd/il>\n"
                             "  target: <'abCde'>" % re_repr,
                             None)],
                           ["test_assert_not_found"])

    def test_assert_hasattr(self):
        self.assert_result(False, 1, 2, 1, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_hasattr",
                             "expected: hasattr('string', 'Strip')",
                             None)],
                           ["test_assert_hasattr"])

    def test_assert_callable(self):
        self.assert_result(False, 1, 2, 1, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_callable",
                             "expected: callable('string')",
                             None)],
                           ["test_assert_callable"])

    def test_assert_call_raise(self):
        self.assert_result(False, 2, 5, 2, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_call_raise",
                             "expected: <exceptions.NameError> is raised\n"
                             " but was: %s() nothing raised" %
                             ("test.test_assertions.nothing_raised"),
                             None),
                            ('F',
                             "TestCase.test_assert_call_raise_different_error",
                             "expected: <exceptions.NameError> is raised\n"
                             " but was: <exceptions.ZeroDivisionError>"
                             "(integer division or modulo by zero)",
                             None)],
                           ["test_assert_call_raise",
                            "test_assert_call_raise_different_error"])

    def test_assert_call_nothing_raised(self):
        self.assert_result(False, 1, 4, 1, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_call_nothing_raised",
                             "expected: %s() nothing raised\n"
                             " but was: <%s>(%s) is raised" % \
                                 ("test.test_assertions."
                                  "raise_zero_division_error",
                                  "exceptions.ZeroDivisionError",
                                  "integer division or modulo by zero"),
                             None)],
                           ["test_assert_call_nothing_raised"])

    def test_assert_run_command(self):
        self.assert_result(False, 2, 2, 2, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_run_command",
                             "expected: <%s> is successfully finished\n"
                             " but was: <%d> is returned as exit code" % \
                                 ("'false'", 1),
                             None),
                            ('F',
                             "TestCase.test_assert_run_command_unknown",
                             "expected: <%s> is successfully ran\n"
                             " but was: <%s>(%s) is raised and failed to ran" \
                                 % ("['unknown', 'arg1', 'arg2']",
                                    "exceptions.OSError",
                                    "[Errno 2] No such file or directory"),
                             None)],
                           ["test_assert_run_command",
                            "test_assert_run_command_unknown"])

    def test_assert_search_syslog_in_calling(self):
        detail = \
            "expected: <%s> is found in <%s>\n" \
            " content: <'.*FIXME!!!.*'>" % \
            ("/fix me!/", "'/var/log/messages'")
        self.assert_result(False, 1, 2, 1, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_search_syslog_in_calling",
                             re.compile(detail),
                             None)],
                           ["test_assert_search_syslog_in_calling"])

    def test_assert_open_file(self):
        self.assert_result(False, 1, 2, 1, 0, 0, 0,
                           [('F',
                             "TestCase.test_assert_open_file",
                             "expected: file('%s') succeeds\n"
                             " but was: <%s>(%s) is raised" % \
                                 (nonexistent_path,
                                  "exceptions.IOError",
                                  "[Errno 2] No such file or directory: '%s'" % \
                                      nonexistent_path),
                             None)],
                           ["test_assert_open_file"])
