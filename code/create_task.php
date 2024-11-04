<?php
    // 連線到資料庫
  require_once('db.php');

  if (isset($_POST['submit'])) {
    $task_id = $_POST['task_id'];
    $task_name = $_POST['task_name'];
    // 創建新資料夾
    //$directory = './index.php'; // 設定要建立資料夾的路徑
    //$path = $directory . '/' . $filename;

   // if (!is_dir($path)) {
        if (mkdir($task_name)) {
            // 將資料夾名稱存入資料庫
            $sql = "INSERT INTO tasks (task_id,task_name) VALUES ('$task_id','$task_name')";

            if ($conn->query($sql) === TRUE) {
                //echo "資料夾 '$filename' 建立成功並已儲存至資料庫.";
                header("Location: /view");
            } /*else {
                echo "Error: " . $sql . "<br>" . $conn->error;
            }*/
        } else {
            echo "無法建立任務.";
        }
    } else {
        echo "任務已經存在.";
}


$conn->close();


?>