import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import csv
import datetime
import os

from scipy.ndimage import gaussian_filter1d

ser = serial.Serial('COM4', 115200)

temps = [[] for _ in range(16)]
temps_smooth = [[] for _ in range(16)]
time_data = []

time_signal_count = 0
start_time = None

def read_and_process_data():
    global time_signal_count, start_time
    
    line = ser.readline().decode('utf-8').strip()
    serial_values = line.split(',')
    
    if len(serial_values) == 17:  # 確保所有17個值都存在 ( ardiuno在一開始接收的時候需要初始畫而遺漏訊號 ) 
        try:
            current_time = float(serial_values[0])
            
            # 如果收到的時間訊號少於五個，則增加計數器但不執行後續操作
            if time_signal_count < 3:
                time_signal_count += 1
                return
            
            if start_time is None:
                start_time = current_time
            
            relative_time = current_time - start_time  # 計算相對時間
            
            time_data.append(relative_time)
            for i in range(16):
                temps[i].append(float(serial_values[i + 1]))
            
            print(f'{relative_time}, ' + ', '.join([f'{serial_values[i+1]}' for i in range(16)]))

        except ValueError as e:
            print(f"數據轉換錯誤: {e}")
    else:
        print(f"接收到不完整的數據: {line} , {len(serial_values)}")
        return 
    
    sigma = 5 
    for i in range(16):
        temps_smooth[i] = gaussian_filter1d(temps[i], sigma=sigma)  # 使用高斯濾波器平滑溫度
        
def update_plot(frame):
    read_and_process_data()
    
    # 只有當時間數據和溫度數據都不為空時才更新圖表
    if time_data and all(temps):
        plt.cla()
        for i in range(16):
            plt.plot(time_data, temps[i], label=f'Temp{i+1}')
        for i in range(16):
            plt.plot(time_data, temps_smooth[i], label=f'Temp{i+1}_smooth')
        plt.xlabel('Time(s)')
        plt.ylabel('Temperature(C)')

        max_temp = max(max(temp_list, default=0) for temp_list in temps)
        
        plt.ylim(20, max_temp + 10)
        plt.legend()
    

def create_csv_with_timestamp():
    try:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')  # 格式化當前時間
        date_folder = datetime.datetime.now().strftime('%Y-%m-%d')  # 當天日期資料夾名稱

        if not os.path.exists(date_folder):
            os.makedirs(date_folder)  
        
        gitignore_path = os.path.join(date_folder, '.gitignore')
        
        if not os.path.exists(gitignore_path):
            with open(gitignore_path, 'w') as gitignore:
                gitignore.write("*")
                gitignore.close()
        
        filename = os.path.join(date_folder, f'arduino_data_{current_time}.csv') 

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Time'] + [f'Temp_{i+1}' for i in range(16)] + [f'Temp_{j+1}_smooth' for j in range(16)])
            for row in zip(time_data, *temps, *temps_smooth):
                writer.writerow(row)
    
        print(f"成功儲存到: {filename}")

    except IOError as e:
        print(f"保存數據到CSV時出錯: {e}")
    except Exception as e:
        print(f"意外錯誤: {e}")

# 函數：在關閉圖表時創建CSV文件並關閉串口
def on_close(event):
    create_csv_with_timestamp()
    ser.close()  # 關閉串口

# 函數：停止動畫並關閉圖表
def stop_animation_and_close():
    ani.event_source.stop()
    plt.close()
    create_csv_with_timestamp()  # 關閉圖表時保存帶有時間戳的CSV文件
    ser.close()  # 關閉串口

# 創建圖表並連接關閉事件以保存CSV
fig, ax = plt.subplots()
fig.canvas.mpl_connect('close_event', on_close)
ani = animation.FuncAnimation(fig, update_plot, interval=1000)  # 每500毫秒更新一次
plt.show()
