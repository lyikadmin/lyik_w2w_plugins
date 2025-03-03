# from unittest.mock import patch
# import pytest
# from generate_pdf_plugins import GeneratePdf
# import json
# import os

# @pytest.mark.asyncio
# async def test_create_aof():
#     pdf_plugin = GeneratePdf()

#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     file_path = os.path.join(current_dir, 'test_json_data2012.json')
#     with open(file_path, 'r') as file:
#         dynamic_data = json.load(file) 
#     dummy_data =  dynamic_data
    
#     # await pdf_plugin.generate_pdf(context={},form_name='aof_form',payload=dummy_data)
#     await pdf_plugin.get_pdf(context={},form_name='aof_form',record=dummy_data,pdf_name='aof_test')

# # @pytest.mark.asyncio
# # async def test_create_cet_dp():
# #     pdf_plugin = GeneratePdf()
# #     await pdf_plugin.generate_pdf(context={},form_name='cet_dp',data={},pdf_name='w2w_cet_dp_form_cust_ID.pdf')


# # @pytest.mark.asyncio
# # async def test_create_ddpi():
# #     pdf_plugin = GeneratePdf()
# #     await pdf_plugin.generate_pdf(context={},form_name='ddpi',data={},pdf_name='w2w_ddpi_form_cust_ID.pdf')


