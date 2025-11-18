#!/usr/bin/env python3
import time
import sys
import math

from unitree_sdk2py.core.channel import ChannelPublisher
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.idl.default import HGLowCmd_, HGMotorCmd_

class G1StanceController:
    def __init__(self):
        self.pub = None
        self.current_pose = [0.0] * 29
        
    def initialize_communication(self):
        """Инициализация связи с роботом"""
        ChannelFactoryInitialize(0, "lo")
        self.pub = ChannelPublisher("rt/lowcmd", HGLowCmd_)
        self.pub.Init()
        print("✓ DDS communication initialized")
    
    def create_safe_command(self):
        """Создание безопасной команды"""
        motor_cmds = []
        for i in range(35):
            motor_cmd = HGMotorCmd_(
                mode=0x0A,  # Position control
                q=0.0, dq=0.0, tau=0.0,
                kp=0.0, kd=0.0, reserve=0
            )
            motor_cmds.append(motor_cmd)
        
        cmd = HGLowCmd_(
            mode_pr=0, mode_machine=1,
            motor_cmd=motor_cmds,
            reserve=[0, 0, 0, 0], crc=0
        )
        cmd.head = [0xFE, 0xEF]
        cmd.level_flag = 0xFF
        return cmd
    
    def smooth_interpolation(self, start_pose, target_pose, duration_seconds=3.0):
        """ПЛАВНОЕ перемещение в целевую позу"""
        steps = int(duration_seconds * 100)  # 100Hz
        cmd = self.create_safe_command()
        
        print(f"🔄 Smooth transition to target pose ({duration_seconds}s)...")
        
        for step in range(steps):
            # Кубическая интерполяция для плавности
            t = step / steps
            smooth_t = t * t * (3.0 - 2.0 * t)  # smoothstep
            
            # Интерполяция всех суставов
            for i in range(29):
                cmd.motor_cmd[i].q = start_pose[i] + (target_pose[i] - start_pose[i]) * smooth_t
                # Постепенное увеличение жесткости
                cmd.motor_cmd[i].kp = 20.0 + (self.get_target_stiffness(i) - 20.0) * smooth_t
                cmd.motor_cmd[i].kd = 1.0 + (self.get_target_damping(i) - 1.0) * smooth_t
            
            self.pub.Write(cmd)
            time.sleep(0.01)
        
        print("✓ Target pose reached")
        return cmd
    
    def get_target_stiffness(self, motor_id):
        """Оптимальная жесткость для каждого мотора"""
        stiffness_map = {
            # Ноги - высокая жесткость для устойчивости
            0: 120, 1: 100, 2: 80,   # L_HIP
            3: 150,                   # L_KNEE (самая высокая)
            4: 120, 5: 100,          # L_ANKLE
            6: 120, 7: 100, 8: 80,   # R_HIP  
            9: 150,                   # R_KNEE
            10: 120, 11: 100,        # R_ANKLE
            # Талия - средняя жесткость
            12: 80, 13: 80, 14: 90,  # WAIST
            # Руки - низкая жесткость
            15: 50, 16: 40, 17: 30, 18: 40,  # L_ARM
            19: 20, 20: 20, 21: 20,          # L_WRIST
            22: 50, 23: 40, 24: 30, 25: 40,  # R_ARM
            26: 20, 27: 20, 28: 20           # R_WRIST
        }
        return stiffness_map.get(motor_id, 60.0)
    
    def get_target_damping(self, motor_id):
        """Оптимальное демпфирование для каждого мотора"""
        damping_ratio = 0.10  # Критическое демпфирование ~10%
        kp = self.get_target_stiffness(motor_id)
        return 2 * damping_ratio * math.sqrt(kp)  # kd = 2 * ζ * √(kp)
    
    def get_upright_pose(self):
        """ИДЕАЛЬНАЯ ПРЯМАЯ СТОЙКА - нейтральные значения"""
        pose = [0.0] * 29
        
        # 🔥 КЛЮЧЕВОЕ: НЕЙТРАЛЬНЫЕ ЗНАЧЕНИЯ ДЛЯ БАЛАНСА
        # Ноги - слегка согнуты для устойчивости
        pose[0] = 0.02   # L_HIP_PITCH
        pose[1] = 0.0    # L_HIP_ROLL  - НЕЙТРАЛЬНО!
        pose[2] = 0.0    # L_HIP_YAW   - НЕЙТРАЛЬНО!
        pose[3] = 0.10   # L_KNEE      - слегка согнуто
        pose[4] = -0.05  # L_ANKLE_PITCH
        pose[5] = 0.0    # L_ANKLE_ROLL - НЕЙТРАЛЬНО!
        
        # Правая нога - симметрично
        pose[6] = 0.02   # R_HIP_PITCH
        pose[7] = 0.0    # R_HIP_ROLL  - НЕЙТРАЛЬНО!
        pose[8] = 0.0    # R_HIP_YAW   - НЕЙТРАЛЬНО!
        pose[9] = 0.10   # R_KNEE
        pose[10] = -0.05 # R_ANKLE_PITCH
        pose[11] = 0.0   # R_ANKLE_ROLL - НЕЙТРАЛЬНО!
        
        # Талия - прямо
        pose[12] = 0.0   # WAIST_YAW
        pose[13] = 0.0   # WAIST_ROLL
        pose[14] = 0.0   # WAIST_PITCH
        
        # Руки - опущены вдоль тела
        pose[15] = 0.0 # L_SHOULDER_PITCH (вниз)
        pose[16] = 0.0   # L_SHOULDER_ROLL
        pose[17] = 0.0   # L_SHOULDER_YAW
        pose[18] = -1.57   # L_ELBOW
        # Запястья - нейтрально
        
        pose[22] = 0.0 # R_SHOULDER_PITCH (вниз)
        pose[23] = 0.0   # R_SHOULDER_ROLL
        pose[24] = 0.0   # R_SHOULDER_YAW  
        pose[25] = 1.57   # R_ELBOW
        
        return pose
    
    def get_athletic_pose(self):
        """АТЛЕТИЧЕСКАЯ СТОЙКА - более устойчивая"""
        pose = self.get_upright_pose()
        
        # Более широкие и согнутые ноги
        pose[1] = 0.15   # L_HIP_ROLL - шире
        pose[3] = 0.20   # L_KNEE - больше сгиб
        pose[7] = -0.15  # R_HIP_ROLL - шире  
        pose[9] = 0.20   # R_KNEE - больше сгиб
        
        # Руки согнуты для баланса
        pose[18] = -1.0  # L_ELBOW согнут
        pose[25] = -1.0  # R_ELBOW согнут
        
        return pose
    
    def get_low_pose(self):
        """НИЗКАЯ СТОЙКА - максимальная устойчивость"""
        pose = self.get_upright_pose()
        
        # Сильно согнутые ноги
        pose[3] = 0.35   # L_KNEE
        pose[9] = 0.35   # R_KNEE
        pose[4] = 0.08   # L_ANKLE_PITCH
        pose[10] = 0.08  # R_ANKLE_PITCH
        
        # Таз слегка назад
        pose[0] = 0.08   # L_HIP_PITCH
        pose[6] = 0.08   # R_HIP_PITCH
        
        return pose

def main():
    controller = G1StanceController()
    controller.initialize_communication()
    
    # Начальная поза (все нули)
    start_pose = [0.0] * 29
    
    print("🤖 G1 Intelligent Stance Controller")
    print("1. Upright Pose - прямая стойка")
    print("2. Athletic Pose - атлетическая стойка") 
    print("3. Low Pose - низкая стойка")
    
    try:
        choice = input("Select pose (1-3, default=1): ").strip()
        
        if choice == "2":
            target_pose = controller.get_athletic_pose()
            print("🏋️ Transition to ATHLETIC pose...")
        elif choice == "3":
            target_pose = controller.get_low_pose() 
            print("🦘 Transition to LOW pose...")
        else:
            target_pose = controller.get_upright_pose()
            print("🧍 Transition to UPRIGHT pose...")
        
        # Плавный переход
        cmd = controller.smooth_interpolation(start_pose, target_pose, 4.0)
        
        print("🎯 Maintaining stance... Press Ctrl+C to stop")
        
        counter = 0
        while True:
            controller.pub.Write(cmd)
            
            if counter % 500 == 0:  # Каждые 5 секунд
                print("✓ Stable stance maintained")
            
            counter += 1
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n🛑 Smooth shutdown...")
        # Плавное уменьшение жесткости
        for step in range(100):
            for i in range(29):
                cmd.motor_cmd[i].kp *= 0.95
                cmd.motor_cmd[i].kd *= 0.95
            controller.pub.Write(cmd)
            time.sleep(0.02)
        print("✅ Shutdown complete")

if __name__ == '__main__':
    main()
