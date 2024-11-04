<?php
header('Content-Type: application/json');

// Retrieve data sent from the Flask application
$parentFolderPath = $_POST['parentFolderPath'];
$newSubfolderName = $_POST['newSubfolderName'];

// Check if the parent folder path and subfolder name are provided
if (!isset($parentFolderPath) || !isset($newSubfolderName)) {
    http_response_code(400); // Bad Request
    echo json_encode(array('error' => 'Missing parentFolderPath or newSubfolderName'));
    exit();
}

// Your logic to create the subfolder
// For demonstration purposes, let's just echo a success message
$response = array('message' => 'Subfolder created successfully: ' . $parentFolderPath . '/' . $newSubfolderName);

// Send the response back to the Flask application
echo json_encode($response);
?>
