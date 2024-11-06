package com.example.myapplication4

import android.app.Dialog
import android.content.DialogInterface
import android.os.Bundle
import android.widget.Button
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import com.google.android.material.snackbar.Snackbar

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }
        val btnToast = findViewById<Button>(R.id.btnToast)
        val btnSnackBar = findViewById<Button>(R.id.btnSnackBar)
        val btnDialog1 = findViewById<Button>(R.id.btnDialog1)
        val btnDialog2 = findViewById<Button>(R.id.btnDialog2)
        val btnDialog3 = findViewById<Button>(R.id.btnDialog3)

        val item = arrayOf("選項1", "選項2", "選項3", "選項4", "選項5")
        btnToast.setOnClickListener{
            showToast("預設 Toast")
        }
        btnSnackBar.setOnClickListener{
            Snackbar.make(it, "按鈕式 SnackBar", Snackbar.LENGTH_SHORT).setAction("按鈕"){
                showToast("已回應")
            }.show()
        }
        btnDialog1.setOnClickListener{
            AlertDialog.Builder(this)
                .setTitle("按鈕式 AlertDialog")
                .setMessage("AlertDialog 內容")
                .setNeutralButton("左按鈕"){ DialogInterface, which->
                    showToast("左按鈕")
                }.setNegativeButton("中按鈕"){ DialogInterface, which->
                    showToast("中按鈕")
                }.setPositiveButton("右按鈕"){ DialogInterface, which->
                    showToast("右按鈕")
                }.show()
        }
        btnDialog2.setOnClickListener{
            AlertDialog.Builder(this)
                .setTitle("列表式 AlertDialog")
                .setItems(item){ DialogInterface,i ->
                    showToast("你選的是${item[i]}")
                }.show()
        }
        btnDialog3.setOnClickListener{
            var position = 0
            AlertDialog.Builder(this)
                .setTitle("單選式 AlertDialog")
                .setSingleChoiceItems(item, 0){ DialogInterface, i ->
                    position = i
                }.setPositiveButton("確定"){ Dialog, which ->
                    showToast("你選的是${item[position]}")
                }.show()
        }
    }
    private fun showToast(msg : String){
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()
    }
}