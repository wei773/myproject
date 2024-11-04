<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $newFolderName = $_POST['newFolderName'];
    $targetDir = './uploads/' . $newFolderName;

    if (!file_exists($targetDir)) {
        mkdir($targetDir, 0777, true);
        echo '父資料夾新增成功';
    } else {
        echo '父資料夾已存在';
    }
}
?>
