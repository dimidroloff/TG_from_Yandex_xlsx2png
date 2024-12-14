import excel2img
import os
import pandas as pd
import openpyxl


def create_folder_structure(base_folder):
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)


def clear_folder(folder):
    for item in os.listdir(folder):
        item_path = os.path.join(folder, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            for sub_item in os.listdir(item_path):
                sub_item_path = os.path.join(item_path, sub_item)
                os.remove(sub_item_path)
            os.rmdir(item_path)


def get_used_range(df):
    """
    Определяет диапазон ячеек в формате Excel для заданного DataFrame.
    """
    if df.empty:
        return "A1:A1"

    # Получение индексов строк и столбцов
    max_row = len(df)
    max_col = len(df.columns)

    # Преобразование номера столбца в буквенное обозначение
    def col_num_to_letter(n):
        string = ""
        while n > 0:
            n, remainder = divmod(n - 1, 26)
            string = chr(65 + remainder) + string
        return string

    end_col = col_num_to_letter(max_col)
    return f"A1:{end_col}{max_row}"


def process_excel_files(input_folder, output_folder):
    create_folder_structure(output_folder)
    clear_folder(output_folder)

    for file_name in os.listdir(input_folder):
        if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
            file_path = os.path.join(input_folder, file_name)
            excel_file = pd.ExcelFile(file_path)
            file_output_folder = os.path.join(output_folder, os.path.splitext(file_name)[0])
            create_folder_structure(file_output_folder)

            for sheet_name in excel_file.sheet_names:
                try:
                    # Читаем данные с листа
                    df = excel_file.parse(sheet_name)

                    # Определяем диапазон данных
                    range_str = get_used_range(df)
                    print(file_path)

                    # Генерация PNG
                    output_image_path = os.path.join(file_output_folder, f"{sheet_name}.png")
                    excel2img.export_img(file_path, output_image_path, sheet_name, range_str)

                except Exception as er:
                    print("Пропуск ", file_path)
                    print(er)
                    print()


# if __name__ == "__main__":
#     input_folder = "temp/123"
#     output_folder = "temp/output"
#     process_excel_files(input_folder, output_folder)
