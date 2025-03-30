Readme.md


# Project Description
This document describes the steps taken to make pihole function on a RasberryPi. 

(Insert description on pi-hole)



## Hardware: 

We acquire a Rasperry Pi 4 with accesories for about $100. Here is a breakdown and links in case you are interested on replicating this project in your own home.

| Item     | Cost($)|
| ----------- | ----------- |
| [Raspberry Pi 4 Model B - 4 GB RAM](https://www.adafruit.com/product/4296)      | 55  |
| [Official Raspberry Pi Power Supply 5.1V 3A with USB C - 1.5 meter long](https://www.adafruit.com/product/4298)      | 7.95  |
| [Official Raspberry Pi Foundation Raspberry Pi 4 Case - Red White](https://www.adafruit.com/product/4301)      | 6  |
| [Micro-HDMI to HDMI Socket Adapter Cable](https://www.adafruit.com/product/1358)      | 7  |
| [SanDisk 256GB Extreme microSDXC UHS-I Memory Card with Adapter](https://www.amazon.com/SanDisk-256GB-Extreme-microSD-Adapter/dp/B07FCR3316/ref=sr_1_3?keywords=class+10+micro+sd+card+256gb+sandisk&qid=1637345032&sr=8-3)      | 40  |

You will also need: 
- Ithernet cable
- Network controller. For our case, we use Unifi


Please note that although this is the software we chose, you could choose cheaper options as this project does not use all the memory card nor capacity available in the hardware. 

## Pi-hole Configuration

#### 1.1) Installing an OS

Based on the steps described in https://pi-hole.net, you can use multiple OS. We decided to use the Ubuntu version for IoT that does not have a server to have a more stable and minimal software layer. This OS requires a ubuntu account as it only supports SSH



Go to [Ubuntu Website](https://ubuntu.com/download/raspberry-pi-core) and download raspberry Pi Ubuntu Server 64B.

    Note: you could probably use the raspberry Pi Ubuntu Server 32B but I would definitely stir away from Raspberry Pi Core, because even through will likely be more stable, it also has bare functions and basic commands as "app get" or "curl" are not available. It is also recommended to have the raspberry pi unit physically connected to ethernet during this process. 

Through the installation process you will need to create an image. You can use the [RasberryPi Imager](https://www.raspberrypi.com/software/) for Mac to flash your drive. 

![RasberryPi Imager Application](images/imager_1.6.2.jpg)


Make sure you enable SSH by running the following commands: 

'''
Type sudo apt-get install openssh-server
Enable the ssh service by typing sudo systemctl enable ssh
Start the ssh service by typing sudo systemctl start ssh
Test it by login into the system using ssh user@server-name
'''
[Code source: Ubuntu Linux install OpenSSH server (Vivek Gite)](https://www.cyberciti.biz/faq/ubuntu-linux-install-openssh-server/)


#### 1.2) Configuring Static IP

We have a network management system in place, so we did it at the network controller level. 


#### 1.3) Installing pihole

Now that you have access to your raspberry Pi, go to [Pihole Github](https://github.com/pi-hole/pi-hole/#one-step-automated-install) and follow the instructions.

![Pihole Installation](images/pihole_installation.jpg)

During the installation it requires to select a Upstream DNS Provider. We selected "Cloudflare (DNSSEC)". We favor this provider because it favors speed and privacy. You can read more about it [here](https://1.1.1.1/dns/). For all other options during the configuration, we chose default values. These options included Web Interface (On), Web Server (On) and Logging (On) among others.

Once the installation is over, you will see a box like in the image below, where you are given IP addresses for your DNS server and the login information for the web console. 

![Final Wizard Screen](images/final-set-up-screen.jpg)

## Post Pi-hole Installation

As the Pi-ole documentation states:  "once the installer has been run, you will need to configure your router to have DHCP clients use Pi-hole as their DNS server which ensures that all devices connecting to your network will have content blocked without any further intervention.

If your router does not support setting the DNS server, you can use Pi-hole's built-in DHCP server; be sure to disable DHCP on your router first (if it has that feature available).

As a last resort, you can manually set each device to use Pi-hole as their DNS server."

In our case, we have Unifi Network Manager. For any other unifi users, you may find a step by step below. or other users, please feel free to skip to the Web Console section.

#### Post Pi-hole Installation for Unify users only

1) Step 1: 

On your Network Unifi console, select "Networks" on the left side. Then click on the network row that will appear on the right side of the console. 
![Set Up](images/configure_unify_step1.png)

2) Step 2: 

Click "Advanced" options.
![Set Up](images/configure_unify_step2.png)

3) Step 3: 

Look for the "DHCP Name Server" section. Select "Manual" from the drop down.
![Set Up](images/configure_unify_step3.png)

4) Step 4: 

Type the IP-4 address provided by the pi-hole wizard. 
![Set Up](images/configure_unify_step4.png)

5) Step 5: 

Repeat the same for the v6 in the appropriate section. Save all changes.
![Set Up](images/configure_unify_step5.png)


## Pi-hole Web Console

If you use the http link provided by the wizard, you can see the web server. I may dig deeper into what is available here once we have enough data flowing, but wanted to share what it partially look like. 

![Web Console](images/web-console.png)