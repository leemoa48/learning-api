import pytest
import asyncio
from cloudstore import upload_doc
import cloudinary.uploader
import os

@pytest.mark.asyncio
async def test_upload_doc_error(monkeypatch):
    """
    Test that upload_doc returns None when cloudinary.uploader.upload raises an exception.
    This simulates an error scenario where the underlying uploader fails.
    """
    def fake_upload(*args, **kwargs):
        raise Exception("Test error")
    
    monkeypatch.setattr(cloudinary.uploader, "upload", fake_upload)
    
    result = await upload_doc("dummy_file", "dummy_name")
    assert result is None

@pytest.mark.asyncio
async def test_upload_doc_success(monkeypatch):
    """
    Test that upload_doc returns the secure_url when cloudinary.uploader.upload
    successfully uploads the file.
    """
    def fake_upload(file, public_id, resource_type, use_filename, unique_filename, pages):
        return {"secure_url": "http://dummy_url/success"}
    
    monkeypatch.setattr(cloudinary.uploader, "upload", fake_upload)
    
    result = await upload_doc("dummy_file", "dummy_name")
    assert result == "http://dummy_url/success"

@pytest.mark.asyncio
async def test_upload_doc_missing_secure_url(monkeypatch):
    """
    Test that upload_doc returns None when the returned dictionary from 
    cloudinary.uploader.upload lacks the "secure_url" key, simulating an unexpected 
    response format.
    """
    def fake_upload(file, public_id, resource_type, use_filename, unique_filename, pages):
        return {"not_secure_url": "http://dummy_url/failure"}
    
    monkeypatch.setattr(cloudinary.uploader, "upload", fake_upload)
    
    result = await upload_doc("dummy_file", "dummy_name")
    assert result is None

@pytest.mark.asyncio
async def test_upload_doc_argument_passing(monkeypatch):
    """
    Test that upload_doc passes the expected arguments to cloudinary.uploader.upload.
    This verifies that the function is called with the correct file, public_id, resource_type,
    use_filename, unique_filename, and pages values.
    """
    captured_args = {}
    def fake_upload(file, public_id, resource_type, use_filename, unique_filename, pages):
        captured_args["file"] = file
        captured_args["public_id"] = public_id
        captured_args["resource_type"] = resource_type
        captured_args["use_filename"] = use_filename
        captured_args["unique_filename"] = unique_filename
        captured_args["pages"] = pages
        return {"secure_url": "http://dummy_url/argument_passing"}
    
    monkeypatch.setattr(cloudinary.uploader, "upload", fake_upload)
    
    file_input = "test_file"
    name_input = "test_name"
    result = await upload_doc(file_input, name_input)
    
    expected_secure_url = "http://dummy_url/argument_passing"
    assert result == expected_secure_url
    assert captured_args["file"] == file_input
    assert captured_args["public_id"] == name_input
    assert captured_args["resource_type"] == "auto"
    assert captured_args["use_filename"] is True
    assert captured_args["unique_filename"] is False
    assert captured_args["pages"] is True

@pytest.mark.asyncio
async def test_upload_doc_secure_url_is_none(monkeypatch):
    """
    Test that upload_doc returns None when the 'secure_url' key exists in the response 
    but its value is None. This covers the scenario where the cloudinary uploader response 
    is malformed (with a None URL) even though the key is present.
    """
    def fake_upload(file, public_id, resource_type, use_filename, unique_filename, pages):
        return {"secure_url": None}
    
    monkeypatch.setattr(cloudinary.uploader, "upload", fake_upload)
    
    result = await upload_doc("dummy_file", "dummy_name")
    assert result is None

@pytest.mark.asyncio
async def test_upload_doc_empty_secure_url(monkeypatch):
    """
    Test that upload_doc returns an empty string when the cloudinary.uploader.upload 
    returns a dictionary with a 'secure_url' key whose value is an empty string.
    This covers the scenario where the URL is present but empty.
    """
    def fake_upload(file, public_id, resource_type, use_filename, unique_filename, pages):
        return {"secure_url": ""}
    
    monkeypatch.setattr(cloudinary.uploader, "upload", fake_upload)
    
    result = await upload_doc("dummy_file", "dummy_name")
    assert result == ""

@pytest.mark.asyncio
async def test_upload_doc_non_dict_response(monkeypatch):
    """
    Test that upload_doc returns None when cloudinary.uploader.upload returns a non-dictionary value.
    This simulates a scenario where the uploader returns an unexpected response type.
    """
    def fake_upload(file, public_id, resource_type, use_filename, unique_filename, pages):
        return "not a dict"
    
    monkeypatch.setattr(cloudinary.uploader, "upload", fake_upload)
    
    result = await upload_doc("dummy_file", "dummy_name")
    assert result is None

@pytest.mark.asyncio
async def test_upload_doc_non_string_secure_url(monkeypatch):
    """
    Test that upload_doc returns the secure_url even if it's not a string.
    This covers the scenario where the returned secure_url value is an unexpected type.
    """
    def fake_upload(file, public_id, resource_type, use_filename, unique_filename, pages):
        return {"secure_url": 12345}  # non-string value
    
    monkeypatch.setattr(cloudinary.uploader, "upload", fake_upload)
    
    result = await upload_doc("dummy_file", "dummy_name")
    assert result == 12345

@pytest.mark.asyncio
async def test_upload_doc_exception_print(monkeypatch):
    """
    Test that upload_doc prints the error message when cloudinary.uploader.upload raises an exception,
    and that the function returns None.
    """
    printed_messages = []
    def fake_print(*args, **kwargs):
        printed_messages.append(" ".join(str(arg) for arg in args))
    
    def fake_upload(*args, **kwargs):
        raise Exception("Test exception print")
    
    monkeypatch.setattr(cloudinary.uploader, "upload", fake_upload)
    monkeypatch.setattr("builtins.print", fake_print)
    
    result = await upload_doc("dummy_file", "dummy_name")
    assert result is None
    assert any("Test exception print" in message for message in printed_messages)

@pytest.mark.asyncio
async def test_upload_doc_concurrent_uploads(monkeypatch):
    """
    Test that multiple concurrent calls to upload_doc return the expected secure_url for each call.
    This verifies that the function works correctly under asynchronous, concurrent usage.
    """
    def fake_upload(file, public_id, resource_type, use_filename, unique_filename, pages):
        return {"secure_url": f"http://dummy_url/{public_id}"}
    
    monkeypatch.setattr(cloudinary.uploader, "upload", fake_upload)
    
    tasks = [upload_doc("dummy_file", f"test_name_{i}") for i in range(5)]
    results = await asyncio.gather(*tasks)
    
    expected_results = [f"http://dummy_url/test_name_{i}" for i in range(5)]
    assert results == expected_results
