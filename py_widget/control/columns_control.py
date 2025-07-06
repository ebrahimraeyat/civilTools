import table_model
from qt_models.columns_control_models import ColumnsControlDelegate, ControlColumns


def check_column(etabs, way=2):
    if way == 1:
        etabs.set_current_unit('kgf', 'cm')
        columns_type_sections_df, columns_type_names_df = etabs.frame_obj.get_columns_type_sections(dataframe=True)
        column_names = etabs.frame_obj.concrete_section_names('Column')
        section_areas = etabs.frame_obj.get_section_area(column_names)
        table_model.show_results(
            columns_type_sections_df,
            model=ControlColumns,
            function=etabs.view.show_frame_with_lable_and_story,
            kwargs = {
                "section_areas": section_areas,
                "custom_delegate": ColumnsControlDelegate,
                "columns_type_names_df": columns_type_names_df,
                'etabs': etabs,
                },
            etabs= etabs,
            json_file_name="Column-Sections",
            result_widget = table_model.ControlColumnResultWidget,
            )
    elif way == 2:
        columns_type_names_df = etabs.frame_obj.stacked_columns_dataframe_by_points()
        columns_type_sections_df = columns_type_names_df.copy(deep=True)
        etabs.set_current_unit('kgf', 'cm')
        section_areas = etabs.frame_obj.get_section_area()
        table_model.show_results(
            columns_type_sections_df,
            model=ControlColumns,
            function=etabs.view.show_frame,
            kwargs = {
                "section_areas": section_areas,
                "custom_delegate": ColumnsControlDelegate,
                "columns_type_names_df": columns_type_names_df,
                'etabs': etabs,
                },
            etabs= etabs,
            json_file_name="Column-Sections",
            result_widget = table_model.ControlColumnResultWidget,
            )
