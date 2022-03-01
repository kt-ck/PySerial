import serial
import serial.tools.list_ports
import time
import wx
class MyFrame(wx.Frame):    
    def __init__(self):
        super().__init__(parent=None, title='串口通信软件',size=(400, 500))
        self.portx = "COM3"
        self.bps = 19200
        #超时设置,None：永远等待操作，0为立即返回请求结果，其他值为等待超时时间(单位为秒）
        self.timex = 2
        self.sleepTime = 0.3
        self.choice = [x[0] for x in list(serial.tools.list_ports.comports())]
        self.serCon = False

        panel = wx.Panel(self)  
        col = wx.BoxSizer(wx.VERTICAL)

        inputRow = wx.BoxSizer(wx.HORIZONTAL)
        portx_text = wx.StaticText(panel, label="选择窗口号")
        font = portx_text.GetFont()
        font.PointSize = 10
        font = font.Bold()
        portx_text.SetFont(font)   
        self.portx_com = wx.ComboBox(panel,choices=self.choice)
        f_text = wx.StaticText(panel, label="波特率")
        font = f_text.GetFont()
        font.PointSize = 10
        font = font.Bold()
        f_text.SetFont(font)
        self.f_textCtrl = wx.TextCtrl(panel)
        inputRow.Add(portx_text,0, wx.ALL | wx.EXPAND, 5 )
        inputRow.Add(self.portx_com,0, wx.ALL | wx.EXPAND, 5 )
        inputRow.Add(f_text,0, wx.ALL | wx.EXPAND, 5 )
        inputRow.Add(self.f_textCtrl,0, wx.ALL | wx.EXPAND, 5 )
        col.Add(inputRow,0, wx.CENTER, 5)

        
        ms_list = []

        for i in range(8):
            ms = wx.StaticText(panel, label="mv")
            ms_font = ms.GetFont()
            ms_font.PointSize = 10
            ms.SetFont(ms_font) 
            ms_list.append(ms)

        self.row_list = []
        self.text_ctrl_list = []
        for i in range(8):
            v_text = wx.StaticText(panel, label="端口{}电压值".format(i + 1))
            font = v_text.GetFont()
            font.PointSize = 10
            font = font.Bold()
            v_text.SetFont(font)   

            v_value = wx.TextCtrl(panel)    
            self.text_ctrl_list.append(v_value)
            row = wx.BoxSizer(wx.HORIZONTAL)
            row.Add(v_text, 0, wx.ALL | wx.EXPAND, 5)
            row.Add(v_value, 0, wx.ALL | wx.EXPAND, 5)
            row.Add(ms_list[i], 0, wx.ALL | wx.EXPAND, 5)
            self.row_list.append(row)

        for i in range(8):
            col.Add(self.row_list[i], 0, wx.CENTER, 5)

        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        self.con_btn = wx.Button(panel,label="连接串口")
        btn_row.Add(self.con_btn, 0, wx.ALL | wx.EXPAND, 5)
        btn = wx.Button(panel,label="发送数据")
        btn_row.Add(btn, 0, wx.ALL | wx.EXPAND, 5)
        self.Bind(wx.EVT_BUTTON, self.onPress,btn)
        self.Bind(wx.EVT_BUTTON, self.conOnPress,self.con_btn)
        col.Add(btn_row, 0, wx.CENTER, 5)
        panel.SetSizer(col)       
        self.Show()

    def conOnPress(self, event):
        if self.serConnect(self.portx_com.GetStringSelection(), self.f_textCtrl.GetValue()):
            self.con_btn.SetLabel("关闭串口")
            self.Bind(wx.EVT_BUTTON, self.disconOnPress,self.con_btn)

    def disconOnPress(self,event):
        self.con_btn.SetLabel("连接串口")
        self.Bind(wx.EVT_BUTTON, self.conOnPress,self.con_btn)
        self.ser.close()

    def serConnect(self,portx,bps):
        if not portx:
            error = wx.MessageDialog(None, "请选择一个窗口号", "错误信息提示", wx.YES_DEFAULT | wx.ICON_QUESTION)
            if error.ShowModal() == wx.ID_YES:  # 如果点击了提示框的确定按钮
                error.Destroy()  # 则关闭提示框
            return False
        
        if not bps:
            error = wx.MessageDialog(None, "请输入波特率", "错误信息提示", wx.YES_DEFAULT | wx.ICON_QUESTION)
            if error.ShowModal() == wx.ID_YES:  # 如果点击了提示框的确定按钮
                error.Destroy()  # 则关闭提示框
            return False

        bps = int(bps)
        print(portx, bps)
        try:
            self.ser = serial.Serial(portx,bps,timeout=self.timex, stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS)
        except Exception as e:
            error = wx.MessageDialog(None, "串口连接失败，很有可能被其他应用占用", "错误信息提示", wx.YES_DEFAULT | wx.ICON_QUESTION)
            if error.ShowModal() == wx.ID_YES:  # 如果点击了提示框的确定按钮
                error.Destroy()  # 则关闭提示框
            return False
        if True == self.ser.is_open:
            tic = int(time.time())
            result = self.ser.write(bytes.fromhex("01"))
            time.sleep(self.sleepTime)
            result = self.ser.write(bytes.fromhex("FF"))
            time.sleep(self.sleepTime)
            result = self.ser.write(bytes.fromhex("FF"))
            time.sleep(self.sleepTime)
            Tflag = False
            # print(ser.in_waiting)
            while int(time.time() - tic) < 2:
                # print(time.time() - tic)
                if self.ser.in_waiting > 0:
                    Tflag = True
                    break
            if not Tflag:
                error = wx.MessageDialog(None, "串口打开失败，很有可能未开启电源", "错误信息提示", wx.YES_DEFAULT | wx.ICON_QUESTION)
                if error.ShowModal() == wx.ID_YES:  # 如果点击了提示框的确定按钮
                    error.Destroy()  # 则关闭提示框
                self.ser.close()
                return False
            else:
                return True
        else:
            error = wx.MessageDialog(None, "串口打开失败", "错误信息提示", wx.YES_DEFAULT | wx.ICON_QUESTION)
            if error.ShowModal() == wx.ID_YES:  # 如果点击了提示框的确定按钮
                error.Destroy()  # 则关闭提示框
            return False
    
    def onPress(self, event):
        # 打开串口，并得到串口对象
        # try:
        #     ser = serial.Serial(portx,bps,timeout=timex, stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS)
        # except Exception as e:
        #     error = wx.MessageDialog(None, "串口连接失败，很有可能被其他应用占用", "错误信息提示", wx.YES_DEFAULT | wx.ICON_QUESTION)
        #     if error.ShowModal() == wx.ID_YES:  # 如果点击了提示框的确定按钮
        #         error.Destroy()  # 则关闭提示框
        #     return
        # if True == ser.is_open:
        #     tic = int(time.time())
        #     result = ser.write(bytes.fromhex("01"))
        #     time.sleep(sleepTime)
        #     result = ser.write(bytes.fromhex("FF"))
        #     time.sleep(sleepTime)
        #     result = ser.write(bytes.fromhex("FF"))
        #     time.sleep(sleepTime)
        #     Tflag = False
        #     # print(ser.in_waiting)
        #     while int(time.time() - tic) < 2:
        #         # print(time.time() - tic)
        #         if ser.in_waiting > 0:
        #             Tflag = True
        #             break
        #     if not Tflag:
        #         error = wx.MessageDialog(None, "串口打开失败，很有可能未开启电源", "错误信息提示", wx.YES_DEFAULT | wx.ICON_QUESTION)
        #         if error.ShowModal() == wx.ID_YES:  # 如果点击了提示框的确定按钮
        #             error.Destroy()  # 则关闭提示框
        #         ser.close()
        #         return
        # else:
        #     ser.close()
        #     error = wx.MessageDialog(None, "串口打开失败", "错误信息提示", wx.YES_DEFAULT | wx.ICON_QUESTION)
        #     if error.ShowModal() == wx.ID_YES:  # 如果点击了提示框的确定按钮
        #         error.Destroy()  # 则关闭提示框
        #         ser.close()
        #     return

        value_list = []
        self.ser.flushInput()
        self.ser.flushOutput()
        for index in range(len(self.text_ctrl_list)):
            value = self.text_ctrl_list[index].GetValue()
            if value:
                value = int(float(value))
                if -5000 <= value <= 5000:
                    value_list.append({"port":index+1,"value": value})
                else:
                    
                    msg = wx.MessageDialog(None, "端口{}电压值不符合要求(-5000mv<=v<=5000mv)".format(index + 1), "信息提示", wx.YES_DEFAULT | wx.ICON_INFORMATION)
                    if msg.ShowModal() == wx.ID_YES:  # 如果点击了提示框的确定按钮
                        msg.Destroy()  # 则关闭提示框
                    return
        print(value_list)
        if len(value_list) == 0:
            
            return
        for each in value_list:
            try:
                v = each["value"]
                v_hex = "{:04x}".format(int(v * (0xFFFF - 0x8000) / 5000 + 0x8000))
                data = "{:02x}".format(each["port"])+ v_hex[2:4]  + v_hex[0:2]
                print(data)
                # 写数据
                for i in range(1):
                    result = self.ser.write(bytes.fromhex(data[0:2]))
                    time.sleep(self.sleepTime)
                    print(self.ser.read().hex())
                    result = self.ser.write(bytes.fromhex(data[2:4]))
                    time.sleep(self.sleepTime)
                    print(self.ser.read().hex())
                    result = self.ser.write(bytes.fromhex(data[4:6]))
                    time.sleep(self.sleepTime)
                    print(self.ser.read().hex())
                    
            except Exception as e:
                # self.ser.close()
                error = wx.MessageDialog(None, "读写数据异常", "错误信息提示", wx.YES_DEFAULT | wx.ICON_QUESTION)
                if error.ShowModal() == wx.ID_YES:  # 如果点击了提示框的确定按钮
                    error.Destroy()  # 则关闭提示框
                    break
                return
        
        # self.ser.close()
        msg = wx.MessageDialog(None, "数据上传成功", "信息提示", wx.YES_DEFAULT | wx.ICON_INFORMATION)
        if msg.ShowModal() == wx.ID_YES:  # 如果点击了提示框的确定按钮
            msg.Destroy()  # 则关闭提示框


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()

