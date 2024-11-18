import unittest
import datetime
from shell_emulator import ShellEmulator  # Предположим, что ваш основной файл называется shell_emulator.py

class TestShellEmulator(unittest.TestCase):

    def setUp(self):
        # Настройка эмулятора для тестов
        self.user = "test_user"
        self.vfs_path = "test_vfs.zip"
        self.logfile = "test_log.xml"
        self.emulator = ShellEmulator(self.user, self.vfs_path, self.logfile, None)
        
        # Создание тестовой виртуальной файловой системы
        self.emulator.vfs = {
            "documents": {
                "file1.txt": None,
                "file2.txt": None,
            },
            "downloads": {
                "image1.jpg": None,
            }
        }
        self.emulator.current_dir = self.emulator.vfs
        self.emulator.history = []

    # Тесты для команды ls
    def test_ls_root_directory(self):
        output = self.emulator.process_command("ls")
        expected_output = "documents\ndownloads"
        self.assertEqual(output, expected_output)

    def test_ls_documents_directory(self):
        self.emulator.current_dir = self.emulator.vfs["documents"]
        output = self.emulator.process_command("ls")
        expected_output = "file1.txt\nfile2.txt"
        self.assertEqual(output, expected_output)

    # Тесты для команды cd
    def test_cd_to_documents(self):
        output = self.emulator.process_command("cd documents")
        self.assertEqual(output, "Changed directory to /documents")
        self.assertEqual(self.emulator.current_dir, self.emulator.vfs["documents"])

    def test_cd_to_invalid_directory(self):
        output = self.emulator.process_command("cd invalid_dir")
        self.assertEqual(output, "Directory not found: invalid_dir")

    # Тесты для команды who
    def test_who_command(self):
        output = self.emulator.process_command("who")
        self.assertEqual(output, self.user)

    def test_who_command_different_user(self):
        new_emulator = ShellEmulator("another_user", self.vfs_path, self.logfile, None)
        output = new_emulator.process_command("who")
        self.assertEqual(output, "another_user")

    # Тесты для команды history
    def test_history_with_no_commands(self):
        output = self.emulator.process_command("history")
        self.assertEqual(output, "")

    def test_history_with_some_commands(self):
        self.emulator.process_command("cd documents")
        self.emulator.process_command("ls")
        output = self.emulator.process_command("history")
        expected_output = "cd documents\nls"
        self.assertEqual(output, expected_output)

    # Тесты для команды date
    def test_date_format(self):
        output = self.emulator.process_command("date")
        try:
            # Проверяем, что дата корректно парсится
            datetime.datetime.strptime(output, '%Y-%m-%d %H:%M:%S')
            date_is_valid = True
        except ValueError:
            date_is_valid = False
        self.assertTrue(date_is_valid)

    def test_date_is_current(self):
        # Проверяем, что дата близка к текущей дате
        output = self.emulator.process_command("date")
        current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Берём только дату (год, месяц, день), чтобы избежать проблем с секундным отличием
        self.assertEqual(output[:10], current_date[:10])

if __name__ == '__main__':
    unittest.main()
