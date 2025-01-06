#!/usr/bin/env python
from samplebase import SampleBase
from rgbmatrix import graphics
from subprocess import check_output
import csv
import time
import mtacalls2
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

stops = {}
with open("/home/display/rpi-rgb-led-matrix/bindings/python/samples/stops.csv", 'r') as file:
    csvreader = csv.reader(file)
    header = next(csvreader)
    for row in csvreader:
        stops.update({row[0]: row[1]})

class GraphicsTest(SampleBase):
    def __init__(self, packet, servicedata, *args, **kwargs):
        super(GraphicsTest, self).__init__(*args, **kwargs)
        self.packet = packet
        self.servicedata = servicedata

    def getcolor(self, trainline):
        colors = {
            "4": graphics.Color(0, 146, 66),
            "5": graphics.Color(0, 146, 66),
            "6": graphics.Color(0, 146, 66),
            "1": graphics.Color(255, 0, 0),
            "2": graphics.Color(255, 0, 0),
            "3": graphics.Color(255, 0, 0),
            "A": graphics.Color(0, 57, 163),
            "C": graphics.Color(0, 57, 163),
            "E": graphics.Color(0, 57, 163),
            "B": graphics.Color(255, 99, 32),
            "D": graphics.Color(255, 99, 32),
            "F": graphics.Color(255, 99, 32),
            "M": graphics.Color(255, 99, 32),
            "N": graphics.Color(255, 255, 0),
            "Q": graphics.Color(255, 255, 0),
            "R": graphics.Color(255, 255, 0),
            "W": graphics.Color(255, 255, 0),
            "G": graphics.Color(107, 187, 78),
            "L": graphics.Color(167, 169, 172),
            "7": graphics.Color(185, 52, 170),
            "J": graphics.Color(165, 42, 42),
            "Z": graphics.Color(165, 42, 42)
        }
        return colors.get(trainline, graphics.Color(255, 255, 255))

    def draw_screen(self, canvas, trains, direction, font, scroll_offsets, max_scroll_width):
        canvas.Clear()

        title = "Uptown" if direction == "N" else "Downtown"
        graphics.DrawText(canvas, font, 1, 7, graphics.Color(255, 255, 255), title)

        traincharspacing = 14
        for idx, train in enumerate(trains[:3]):
            color = self.getcolor(train[0])
            train_name = str(train[0])
            stop_name = stops.get(train[2], "Unknown Stop")
            time_to_arrival = str(train[1])

            # Calculate scrolling offset for the stop name
            scroll_offset = scroll_offsets[idx]
            if len(stop_name) > max_scroll_width:
                visible_stop_name = stop_name[scroll_offset:scroll_offset + max_scroll_width]
                scroll_offsets[idx] = (scroll_offset + 1) % (len(stop_name) - max_scroll_width + 1)
            else:
                visible_stop_name = stop_name

            graphics.DrawText(canvas, font, 2, traincharspacing, color, train_name) # Train Line
            graphics.DrawText(canvas, font, 8, traincharspacing, graphics.Color(255, 255, 255), visible_stop_name) # Last Stop
            graphics.DrawText(canvas, font, 55, traincharspacing, color, time_to_arrival)  # Arrival Time

            traincharspacing += 8  # Increment Train Spacing for next train

        self.matrix.SwapOnVSync(canvas)


    def run(self):
        canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("../../../fonts/5x8.bdf")

        max_scroll_width = 9  # Width in characters for stop name display
        scroll_offsets_north = [0, 0, 0]
        scroll_offsets_south = [0, 0, 0]

        for subpacket in self.packet:
            uptown_trains = [train for train in subpacket if train[2][3] == "N"]
            downtown_trains = [train for train in subpacket if train[2][3] == "S"]

            for _ in range(30):
                self.draw_screen(canvas, uptown_trains, "N", font, scroll_offsets_north, max_scroll_width)
                time.sleep(0.4) # Scroll speed

            for _ in range(30):
                self.draw_screen(canvas, downtown_trains, "S", font, scroll_offsets_south, max_scroll_width)
                time.sleep(0.4) # Scroll speed

while True:
    if __name__ == "__main__":
        worked=0
        while worked==0:
            try:
                #D17 is Herald Square BDFM
                #R17 is Herald Square NRQW
                packet=mtacalls2.totalstationtimes(["D17", "R17"])
                servicedata=mtacalls2.procservicedata()
                worked=1
            except:
                print("rebooting in 30 seconds")
                time.sleep(30)
                subprocess.Popen('sudo reboot -n', shell=True)              
        
        graphics_test = GraphicsTest(packet, servicedata)

        if (not graphics_test.process()):
            print("isrunning")