package com.starlink.bypass;

import android.app.Activity;
import android.content.Intent;
import android.net.VpnService;
import android.os.Bundle;
import android.widget.Button;
import android.widget.Toast;

public class MainActivity extends Activity {
    private static final int VPN_CODE = 1;
    private boolean active = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button btn = findViewById(R.id.connectBtn);
        btn.setOnClickListener(v -> {
            if (!active) {
                Intent intent = VpnService.prepare(this);
                if (intent != null) startActivityForResult(intent, VPN_CODE);
                else onActivityResult(VPN_CODE, RESULT_OK, null);
            } else {
                stopService(new Intent(this, BypassVpnService.class));
                btn.setText("ПОДКЛЮЧИТЬ");
                active = false;
            }
        });
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == VPN_CODE && resultCode == RESULT_OK) {
            startService(new Intent(this, BypassVpnService.class));
            Button btn = findViewById(R.id.connectBtn);
            btn.setText("ОТКЛЮЧИТЬ");
            active = true;
            Toast.makeText(this, "Обход запущен!", Toast.LENGTH_SHORT).show();
        }
    }
}
