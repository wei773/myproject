<?php
// 在此获取数据库连接
$pdo = new PDO("mysql:host=localhost;dbname=awds", "root", "");

// 查询数据库以获取任务数据
$query = $pdo->query("SELECT * FROM views");
$tasks = $query->fetchAll(PDO::FETCH_ASSOC);

// 输出数据为 JSON
header('Content-Type: application/json');
echo json_encode($tasks);
exit;
?>
