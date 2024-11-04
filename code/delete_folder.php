<?php
// Ensure that the request is a POST request
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Get the folder path from the POST data
    $folderPath = $_POST["folderPath"];

    // Perform the deletion operation
    if (deleteFolder($folderPath)) {
        echo "資料夾已成功刪除";
    } else {
        echo "無法刪除資料夾";
    }
} else {
    // Handle invalid request method
    echo "Invalid request method";
}

function deleteFolder($folderPath) {
    // Implement your folder deletion logic here
    // Ensure proper validation and security measures
    
    try {
        // Sample deletion logic using rmdir (remove directory)
        if (is_dir($folderPath)) {
            rmdir($folderPath);
            return true;
        } else {
            return false;
        }
    } catch (Exception $e) {
        // Handle exceptions if necessary
        return false;
    }
}
?>
