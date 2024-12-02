# Ref : https://cloud.tencent.com/developer/article/2324252 簡單範例
# 畫不了動畫看這個 : https://blog.csdn.net/weixin_39278265/article/details/84060864
import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import csv
import datetime
import pyttsx3

# 配置串口和波特率。將 'COM4' 替換為你的串口。
ser = serial.Serial('COM4', 115200)

# 初始化列表來存儲溫度數據
temps1 = []
temps2 = []
temps3 = []
temps4 = []
temps5 = []
temps6 = []
temps7 = []
temps8 = []
time_data = []

# 設置計數器來跟踪收到的時間訊號數量
time_signal_count = 0
start_time = None

# 初始化語音引擎
engine = pyttsx3.init()
rate = engine.getProperty('rate')  # 獲取當前講話速度
engine.setProperty('rate', rate + 100)  # 減慢講話速度，數值越小速度越慢

# 設置更新計數器
update_count = 0

# 函數：讀取並處理數據
def read_and_process_data():
    global time_signal_count, start_time
    
    line = ser.readline().decode('utf-8').strip()
    temps = line.split(',')
    
    if len(temps) == 9:  # 確保所有9個值都存在 ( ardiuno在一開始接收的時候需要初始畫而遺漏訊號 ) 
        try:
            current_time = float(temps[0])
            
            # 如果收到的時間訊號少於五個，則增加計數器但不執行後續操作
            if time_signal_count < 3:
                time_signal_count += 1
                return
            
            if start_time is None:
                start_time = current_time
            
            relative_time = current_time - start_time  # 計算相對時間
            
            time_data.append(relative_time)
            temps1.append(float(temps[1]))
            temps2.append(float(temps[2]))
            temps3.append(float(temps[3]))
            temps4.append(float(temps[4]))
            temps5.append(float(temps[5]))
            temps6.append(float(temps[6]))
            temps7.append(float(temps[7]))
            temps8.append(float(temps[8]))
            
            # 打印數據以進行驗證
            print(f'Time: {relative_time:.2f}, [1]: {temps[1]}, [2]: {temps[2]}, [3]: {temps[3]}, [4]: {temps[4]}, [5]: {temps[5]}, [6]: {temps[6]}, [7]: {temps[7]}, [8]: {temps[8]}')
        
        except ValueError as e:
            print(f"數據轉換錯誤: {e}")
    else:
        print(f"接收到不完整的數據: {line} , {len(temps)}")
        return  # 如果接收到不完整數據，直接返回，不執行後面的操作

# 函數：說出最高溫度
def speak_max_temp():
    max_temp = max(max(temps1, default=0), max(temps2, default=0), max(temps3, default=0),
                   max(temps4, default=0), max(temps5, default=0), max(temps6, default=0),
                   max(temps7, default=0), max(temps8, default=0))
    engine.say(f"{int(max_temp)}")
    engine.runAndWait()

# 函數：更新圖表
def update_plot(frame):
    global update_count
    read_and_process_data()
    
    # 只有當時間數據和溫度數據都不為空時才更新圖表
    if time_data and temps1 and temps2 and temps3 and temps4 and temps5 and temps6 and temps7 and temps8:
        plt.cla()
        plt.plot(time_data, temps1, label='Temp1')
        plt.plot(time_data, temps2, label='Temp2')
        plt.plot(time_data, temps3, label='Temp3')
        plt.plot(time_data, temps4, label='Temp4')
        plt.plot(time_data, temps5, label='Temp5')
        plt.plot(time_data, temps6, label='Temp6')
        plt.plot(time_data, temps7, label='Temp7')
        plt.plot(time_data, temps8, label='Temp8')
        plt.xlabel('Time(s)')
        plt.ylabel('Temperature(C)')
        
        # 計算所有列表中的最高溫度
        max_temp = max(max(temps1, default=0), max(temps2, default=0), max(temps3, default=0),
                       max(temps4, default=0), max(temps5, default=0), max(temps6, default=0),
                       max(temps7, default=0), max(temps8, default=0))
        
        plt.ylim(20, max_temp + 10)  # 動態設置y軸範圍
        plt.legend()
        
        
        # 每更新10次圖表才說一次最高溫度
        update_count += 1
        if update_count >= 10:
            update_count = 0

# 函數：帶有當前時間戳的文件名創建CSV文件
def create_csv_with_timestamp():
    try:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')  # 格式化當前時間
        filename = f'arduino_data_{current_time}.csv'  # 構建帶有時間戳的文件名
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Time', 'Temp_1', 'Temp_2', 'Temp_3', 'Temp_4', 'Temp_5', 'Temp_6', 'Temp_7', 'Temp_8'])
            for x, T1, T2, T3, T4, T5, T6, T7, T8 in zip(time_data, temps1, temps2, temps3, temps4, temps5, temps6, temps7, temps8):
                writer.writerow([x, T1, T2, T3, T4, T5, T6, T7, T8])
        print(f"數據成功保存到 '{filename}'.")
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
ani = animation.FuncAnimation(fig, update_plot, interval=100)  # 每500毫秒更新一次
plt.show()
