package com.example.myapplication2

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.RadioButton
import android.widget.RadioGroup
import android.widget.TextView
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.os.bundleOf
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat

class SecActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_sec)
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }
        val edDrink = findViewById<TextView>(R.id.edDrink)
        val rgSugar = findViewById<RadioGroup>(R.id.rgSugar)
        val rgIce = findViewById<RadioGroup>(R.id.rgIce)
        val btnSend = findViewById<Button>(R.id.btnSend)

        btnSend.setOnClickListener{
            if (edDrink.text.isEmpty()){
                Toast.makeText(this, "請輸入飲料名稱", Toast.LENGTH_SHORT).show()
            }else{
                val b = bundleOf(
                    "drink" to edDrink.text.toString(),
                    "sugar" to rgSugar.findViewById<RadioButton>(rgSugar.checkedRadioButtonId).text.toString(),
                    "ice" to rgIce.findViewById<RadioButton>(rgIce.checkedRadioButtonId).text.toString()
                )
                val i = Intent().putExtras(b)
                setResult(RESULT_OK,i)
                finish()
            }
        }
    }
}