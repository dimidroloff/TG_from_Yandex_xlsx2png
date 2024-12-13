import excel2img
import os
import pandas as pd


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

def index_to_excel_col(col_idx):
    col = ""
    while col_idx >= 0:
        col = chr(col_idx % 26 + 65) + col
        col_idx = col_idx // 26 - 1
    return col

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
                print(file_path)
                try:
                    # Читаем данные с листа
                    df = excel_file.parse(sheet_name)
                    min_row = df.first_valid_index()
                    max_row = df.last_valid_index()

                    # Для столбцов находим минимальные и максимальные индексы, используя .first_valid_index()
                    min_col = df.columns[df.notna().any()].min()
                    max_col = df.columns[df.notna().any()].max()

                    # Преобразуем индексы в Excel координаты
                    min_col_excel = index_to_excel_col(df.columns.get_loc(min_col))
                    max_col_excel = index_to_excel_col(df.columns.get_loc(max_col))
                    min_row_excel = min_row + 1  # индексы строк начинаются с 1
                    max_row_excel = max_row + 1

                    # Формируем диапазон
                    range_str = f"{min_col_excel}{min_row_excel}:{max_col_excel}{max_row_excel}"

                    sheet_with_range = f"{sheet_name}!{range_str}"
                    range_str = "A1:AU50"
                    print(range_str)

                    output_image_path = os.path.join(file_output_folder, f"{sheet_name}.png")
                    excel2img.export_img(file_path, output_image_path, sheet_name, range_str)
                except Exception as er:
                    print("Пропуск ", file_path)
                    print(er)
                    print()


if __name__ == "__main__":
    input_folder = "temp/123"
    output_folder = "temp/output"
    process_excel_files(input_folder, output_folder)
