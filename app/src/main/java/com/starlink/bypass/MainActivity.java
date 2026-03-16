package com.starlink.bypass;

import android.net.VpnService;
import android.os.ParcelFileDescriptor;
import java.io.*;
import java.net.*;

public class BypassVpnService extends VpnService {
    private ParcelFileDescriptor vpnInterface;
    private Thread proxyThread;

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        // 1. Настраиваем VPN-интерфейс
        Builder builder = new Builder();
        vpnInterface = builder.setMtu(1500)
                .addAddress("10.0.0.2", 32)
                .addRoute("0.0.0.0", 0) // Перехватываем весь трафик
                .addDnsServer("8.8.8.8")
                .setSession("StarlinkBypass")
                .establish();

        // 2. Запускаем наш Java-движок обхода в отдельном потоке
        proxyThread = new Thread(() -> {
            try {
                ServerSocket serverSocket = new ServerSocket(8080);
                while (!Thread.interrupted()) {
                    Socket client = serverSocket.accept();
                    new Thread(() -> handleDpiBypass(client)).start();
                }
            } catch (IOException e) { e.printStackTrace(); }
        });
        proxyThread.start();

        return START_STICKY;
    }

    private void handleDpiBypass(Socket client) {
        try (InputStream in = client.getInputStream(); OutputStream out = client.getOutputStream()) {
            // Читаем запрос (тут логика нашего прокси из блокнота)
            byte[] buf = new byte[16384];
            int n = in.read(buf);
            if (n <= 0) return;
            
            String req = new String(buf, 0, n);
            if (req.startsWith("CONNECT")) {
                String host = req.split(" ")[1].split(":")[0];
                int port = Integer.parseInt(req.split(" ")[1].split(":")[1]);
                
                out.write("HTTP/1.1 200 Connection Established\r\n\r\n".getBytes());
                
                try (Socket remote = new Socket(host, port);
                     InputStream rIn = remote.getInputStream();
                     OutputStream rOut = remote.getOutputStream()) {
                    
                    // Поток от YouTube к нам
                    new Thread(() -> { try { rIn.transferTo(out); } catch (Exception e) {} }).start();

                    // Поток от нас к YouTube (ШИНКОВКА)
                    int len;
                    while ((len = in.read(buf)) != -1) {
                        if (buf[0] == 0x16) { // TLS ClientHello
                            rOut.write(buf[0]); // Отправляем 1 байт
                            rOut.flush();
                            rOut.write(buf, 1, len - 1); // Отправляем остальное
                        } else {
                            rOut.write(buf, 0, len);
                        }
                        rOut.flush();
                    }
                }
            }
        } catch (Exception e) {}
    }

    @Override
    public void onDestroy() {
        if (proxyThread != null) proxyThread.interrupt();
        try { if (vpnInterface != null) vpnInterface.close(); } catch (Exception e) {}
        super.onDestroy();
    }
}
