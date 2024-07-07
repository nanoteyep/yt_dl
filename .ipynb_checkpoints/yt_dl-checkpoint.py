import os
import random
import cv2

# mouse click event function
class ClickEventHandler:
    def __init__(self):
        self.drag_detected = False
        self.dragging = False
        self.start_point = None
        self.end_point = None
        self.rectangles = []
        self.mouse_x = 0
        self.mouse_y = 0
        
    def mouse_callback(self, event, x, y, flags, param):
        self.mouse_x = x
        self.mouse_y = y

        # if the event is mouse left push
        if event == cv2.EVENT_LBUTTONDOWN:
            self.dragging = True
            self.start_point = (x, y)
            self.end_point = None
            print(f"Drag started at: ({x}, {y})")
        # if the event is mouse left up
        elif event == cv2.EVENT_LBUTTONUP:
            if self.dragging:
                self.dragging = False
                self.end_point = (x, y)
                print(f"Drag ended at: ({x}, {y})")
                # calculate the starting x, y position and width, height
                if self.end_point[0] >= self.start_point[0]:
                    x = self.start_point[0]
                    width = self.end_point[0] - self.start_point[0]
                else:
                    x = self.end_point[0]
                    width = self.start_point[0] - self.end_point[0]
                if self.end_point[1] >= self.start_point[1]:
                    y = self.start_point[1]
                    height = self.end_point[1] - self.start_point[1]
                else:
                    y = self.end_point[1]
                    height = self.start_point[1] - self.end_point[1]
                
                self.rectangles.append((x, y, width, height))
                self.drag_detected = True

    # display the coordinate of your mouse position
    def display_with_coordinates(self, window_name, frame):
        display_frame = frame.copy()
        cv2.putText(display_frame, f"({self.mouse_x}, {self.mouse_y})", 
                    (self.mouse_x, self.mouse_y), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.5, (255, 0, 0), 1, cv2.LINE_AA)
         # Draw crosshair lines
        cv2.line(display_frame, (self.mouse_x, 0), (self.mouse_x, display_frame.shape[0]), (0, 255, 0), 1)
        cv2.line(display_frame, (0, self.mouse_y), (display_frame.shape[1], self.mouse_y), (0, 255, 0), 1)
        cv2.imshow(window_name, display_frame)

    def coord_save(self):
        with open('click_coordinates.csv', mode='w') as file:
                for comp in self.rectangles:
                    file.write(f"{comp[0]},{comp[1]},{comp[2]},{comp[3]}\n")
        print("Coordinates saved to click_coordinates.csv")
    
# video downloader
def video_dl(address, output_path):
    print("Downloading the video")
    os.system(f"yt-dlp {address} -o {output_path}")
    return output_path

# open the image that randomly sellected from the video, get the coordinate
def select_animal_coord(num_frames, video_name="0"):
    # open the video
    cap = cv2.VideoCapture(f"./{video_name}/{video_name}.mp4")
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    handler = ClickEventHandler()

    done = 0
    while done < num_frames:
        # divide the total frames into the regions and randomly select the frame in the region
        regions = frame_count // num_frames
        frames = [(idx*regions)+random.randrange(0,regions) for idx in range(num_frames)]
    
        for frame in frames:
            # if you already finish the work then end the loop
            if done >= num_frames:
                break
                
            # go to the frmae
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
            ret, img = cap.read()

            # open the selected image and wait until you press ESC or click the image
            window_name = f'Frame {frame}'
            cv2.imshow(window_name, img)
            cv2.setMouseCallback(window_name, handler.mouse_callback)
            # 27 is ESC
            while True:
                handler.display_with_coordinates(window_name, img)
                key = cv2.waitKey(30)
                if handler.drag_detected:
                    handler.drag_detected = False

                    # if there is no /video_name/images directory, make new directory
                    img_dir = f"./{video_name}/images/"
                    if not os.path.exists(img_dir):
                        os.makedirs(img_dir)
                    cv2.imwrite(img_dir+f"{done+1}.jpg", img)
                    cv2.destroyAllWindows()
                    done += 1
                    break
                if key == 27:
                    cv2.destroyAllWindows()
                    break
    handler.coord_save()

# crop the image using Click_coordinate.csv
def crop_img(csv_path="./click_coordinates.csv", video_name="0"):
    # find the original image of the videos
    path = f"./{video_name}/images/"
    fileEx = ".jpg"
    file_lists = [file for file in os.listdir(path) if file.endswith(fileEx)]

    # read the x,y,width,height information from csv and crop the image and save it
    with open(csv_path, mode='r') as lines:
        for idx,line in enumerate(lines):
            row = line.strip().split(',')
            x, y = int(row[0]), int(row[1])
            width, height = int(row[2]), int(row[3])
            img = cv2.imread(path+file_lists[idx])
            cropped_img = img[y: y + height, x: x + width]
            img_dir = f"./{video_name}/cropped_images/"
            if not os.path.exists(img_dir):
                os.makedirs(img_dir)
            cv2.imwrite(img_dir + f"/{idx+1}.jpg", cropped_img)
            print(f"image {idx+1} is cropped")

# main function
def yt_dl(yt_address, num_frames, video_name="0"):
    video_path = video_dl(yt_address, output_path=f"./{video_name}/{video_name}.mp4")
    select_animal_coord(num_frames, video_name=video_name)
    crop_img(video_name=video_name)