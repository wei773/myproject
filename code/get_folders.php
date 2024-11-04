<?php
function listFolders($folderPath) {
    $folders = glob($folderPath . '*/', GLOB_ONLYDIR);

    if (empty($folders)) {
        return '';
    }

    $html = '<div class="subfolders">';
    foreach ($folders as $folder) {
        $folderName = basename($folder);
        $html .= '<div class="folder" data-path="' . $folder . '"><span class="toggle-icon">▶</span>' . $folderName . '</div>';
        $html .= listFolders($folder); // 遞迴處理子資料夾
    }
    $html .= '</div>';

    return $html;
}

$rootPath = './uploads/';
$folders = glob($rootPath . '*/', GLOB_ONLYDIR);

if (empty($folders)) {
    echo 'no folders found';
} else {
    foreach ($folders as $folder) {
        $folderName = basename($folder);
        echo '<div class="folder" data-path="' . $folder . '"><span class="toggle-icon">▶</span>' . $folderName . '</div>';
        echo listFolders($folder);
    }
}
?>
