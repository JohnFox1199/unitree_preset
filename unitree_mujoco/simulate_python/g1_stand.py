#!/usr/bin/env python3
import time
import sys

from unitree_sdk2py.core.channel import ChannelPublisher
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.idl.default import HGLowCmd_, HGMotorCmd_

def main():
    print("=== G1 Back-Balanced Standing ===")
    print("Pelvis and spine shifted BACK to counterbalance head/arms")
    
    # Инициализация DDS коммуникации с доменом 0 (как в симуляторе)
    ChannelFactoryInitialize(0, "lo")
    # Создаем публикатор для отправки команд в канал "rt/lowcmd"
    pub = ChannelPublisher("rt/lowcmd", HGLowCmd_)
    pub.Init()
    
    # Создаем список команд для всех 35 моторов робота G1
    motor_cmds = []
    for i in range(35):
        # Создаем команду для каждого мотора с начальными параметрами
        motor_cmd = HGMotorCmd_(
            mode=0x0A,    # Режим позиционного контроля (motor wants to reach target position q)
            q=0.0,        # Целевая позиция мотора в радианах (target joint angle in radians)
            dq=0.0,       # Целевая скорость мотора (target velocity)
            tau=0.0,      # Крутящий момент (torque)
            kp=0.0,       # Коэффициент жесткости - сила удержания позиции (position stiffness gain)
            kd=0.0,       # Коэффициент демпфирования - подавление колебаний (velocity damping gain)
            reserve=0     # Резервное поле (reserved field)
        )
        motor_cmds.append(motor_cmd)
    
    # Создаем основную команду управления роботом
    cmd = HGLowCmd_(
        mode_pr=0,              # Режим работы (operation mode)
        mode_machine=1,         # Версия робота: 1 = 23DOF версия (robot version)
        motor_cmd=motor_cmds,   # Список команд для всех моторов (list of motor commands)
        reserve=[0, 0, 0, 0],   # Резервные поля (reserved fields)
        crc=0                   # Контрольная сумма (checksum)
    )
    cmd.head = [0xFE, 0xEF]     # Заголовок команды (command header)
    cmd.level_flag = 0xFF       # Флаг уровня (level flag)
    
    print("Configuring BACK-BALANCED pose...")
    
# ==========================================================================
# НОГИ: Исправленные значения для устойчивости
# ==========================================================================

# Левая нога
    cmd.motor_cmd[0].q = -1.92     # L_HIP_PITCH - таз СЛЕГКА вперед для баланса
    cmd.motor_cmd[0].kp = 300.0   # Жесткость
    cmd.motor_cmd[0].kd = 3.0     # УМЕНЬШЕНО демпфирование (было 8.0)

    cmd.motor_cmd[1].q = 0.0      # L_HIP_ROLL - НЕЙТРАЛЬНО (было 0.15 - это разводило ноги!)
    cmd.motor_cmd[1].kp = 300.0   # Жесткость
    cmd.motor_cmd[1].kd = 3.0     # УМЕНЬШЕНО демпфирование

    cmd.motor_cmd[2].q = 0.0      # L_HIP_YAW - НЕЙТРАЛЬНО (было 0.10 - это скручивало ноги!)
    cmd.motor_cmd[2].kp = 280.0    # Жесткость
    cmd.motor_cmd[2].kd = 2.0     # УМЕНЬШЕНО демпфирование

    cmd.motor_cmd[3].q = 2.2     # L_KNEE - сгиб колена
    cmd.motor_cmd[3].kp = 320.0   # ВЫСОКАЯ жесткость для опоры
    cmd.motor_cmd[3].kd = 4.0     # УМЕНЬШЕНО демпфирование (было 8.0)

    cmd.motor_cmd[4].q = -0.80    # L_ANKLE_PITCH - стопа параллельно полу
    cmd.motor_cmd[4].kp = 300.0   # Жесткость
    cmd.motor_cmd[4].kd = 3.0     # УМЕНЬШЕНО демпфирование

    cmd.motor_cmd[5].q = 0.0      # L_ANKLE_ROLL - НЕЙТРАЛЬНО (было -0.18 - это наклоняло стопу!)
    cmd.motor_cmd[5].kp = 300.0   # Жесткость
    cmd.motor_cmd[5].kd = 3.0     # УМЕНЬШЕНО демпфирование

# Правая нога - СИММЕТРИЧНО левой
    cmd.motor_cmd[6].q = -1.92     # R_HIP_PITCH
    cmd.motor_cmd[6].kp = 300.0
    cmd.motor_cmd[6].kd = 3.0

    cmd.motor_cmd[7].q = 0.0      # R_HIP_ROLL - НЕЙТРАЛЬНО (было -0.15 - это разводило ноги!)
    cmd.motor_cmd[7].kp = 300.0
    cmd.motor_cmd[7].kd = 3.0

    cmd.motor_cmd[8].q = 0.0      # R_HIP_YAW - НЕЙТРАЛЬНО
    cmd.motor_cmd[8].kp = 280.0
    cmd.motor_cmd[8].kd = 2.0

    cmd.motor_cmd[9].q = 2.2     # R_KNEE
    cmd.motor_cmd[9].kp = 320.0
    cmd.motor_cmd[9].kd = 4.0

    cmd.motor_cmd[10].q = -0.80   # R_ANKLE_PITCH
    cmd.motor_cmd[10].kp = 300.0
    cmd.motor_cmd[10].kd = 3.0

    cmd.motor_cmd[11].q = 0.0     # R_ANKLE_ROLL - НЕЙТРАЛЬНО (было 0.18 - это наклоняло стопу!)
    cmd.motor_cmd[11].kp = 300.0
    cmd.motor_cmd[11].kd = 3.0

# ==========================================================================
# ТАЗ И СПИНА: Нейтральное положение
# ==========================================================================

    cmd.motor_cmd[12].q = 0.0     # WAIST_YAW - прямо
    cmd.motor_cmd[12].kp = 380.0   # Жесткость
    cmd.motor_cmd[12].kd = 2.5    # Демпфирование

    cmd.motor_cmd[13].q = 0.0     # WAIST_ROLL - прямо
    cmd.motor_cmd[13].kp = 380.0   # Жесткость
    cmd.motor_cmd[13].kd = 2.5    # УМЕНЬШЕНО демпфирование (было 8.0)

    cmd.motor_cmd[14].q = 0.00     # WAIST_PITCH - прямо (было 0.08 - это наклоняло вперед!)
    cmd.motor_cmd[14].kp = 380.0   # Жесткость
    cmd.motor_cmd[14].kd = 2.5    # Демпфирование

# ==========================================================================
# РУКИ: Опущены по швам с правильными значениями
# ==========================================================================

# Левая рука - ОПУЩЕНА по шву
    cmd.motor_cmd[15].q = 0.0   # L_SHOULDER_PITCH - ОПУЩЕНО ВНИЗ (было 0.25 - это вперед!)
    cmd.motor_cmd[15].kp = 360.0   # Жесткость
    cmd.motor_cmd[15].kd = 2.0    # УМЕНЬШЕНО демпфирование (было 8.0)

    cmd.motor_cmd[16].q = 0.0     # L_SHOULDER_ROLL - НЕЙТРАЛЬНО (было 0.23 - это поднято!)
    cmd.motor_cmd[16].kp = 360.0   # Жесткость
    cmd.motor_cmd[16].kd = 2.0    # УМЕНЬШЕНО демпфирование

    cmd.motor_cmd[17].q = 0.0     # L_SHOULDER_YAW - НЕЙТРАЛЬНО
    cmd.motor_cmd[17].kp = 340.0   # Жесткость
    cmd.motor_cmd[17].kd = 1.5    # УМЕНЬШЕНО демпфирование

    cmd.motor_cmd[18].q = 0.97     # L_ELBOW - РАЗОГНУТ (было 1.00 - это согнуто!)
    cmd.motor_cmd[18].kp = 350.0   # Жесткость
    cmd.motor_cmd[18].kd = 2.0    # УМЕНЬШЕНО демпфирование

    cmd.motor_cmd[19].q = 0.0     # L_WRIST_ROLL
    cmd.motor_cmd[19].kp = 330.0   # НИЗКАЯ жесткость
    cmd.motor_cmd[19].kd = 1.0    # НИЗКОЕ демпфирование

    cmd.motor_cmd[20].q = 0.0     # L_WRIST_PITCH
    cmd.motor_cmd[20].kp = 330.0
    cmd.motor_cmd[20].kd = 1.0

    cmd.motor_cmd[21].q = 0.0     # L_WRIST_YAW
    cmd.motor_cmd[21].kp = 330.0
    cmd.motor_cmd[21].kd = 1.0

# Правая рука - СИММЕТРИЧНО левой
    cmd.motor_cmd[22].q = 0.0   # R_SHOULDER_PITCH - ОПУЩЕНО ВНИЗ
    cmd.motor_cmd[22].kp = 360.0
    cmd.motor_cmd[22].kd = 2.0

    cmd.motor_cmd[23].q = 0.0     # R_SHOULDER_ROLL - НЕЙТРАЛЬНО (было -0.23 - это поднято!)
    cmd.motor_cmd[23].kp = 360.0
    cmd.motor_cmd[23].kd = 2.0

    cmd.motor_cmd[24].q = 0.0     # R_SHOULDER_YAW - НЕЙТРАЛЬНО
    cmd.motor_cmd[24].kp = 340.0
    cmd.motor_cmd[24].kd = 1.5

    cmd.motor_cmd[25].q = 0.97     # R_ELBOW - РАЗОГНУТ (было 1.0 - это согнуто!)
    cmd.motor_cmd[25].kp = 350.0
    cmd.motor_cmd[25].kd = 2.0

    cmd.motor_cmd[26].q = 0.0     # R_WRIST_ROLL
    cmd.motor_cmd[26].kp = 330.0
    cmd.motor_cmd[26].kd = 1.0

    cmd.motor_cmd[27].q = 0.0     # R_WRIST_PITCH
    cmd.motor_cmd[27].kp = 330.0
    cmd.motor_cmd[27].kd = 1.0

    cmd.motor_cmd[28].q = 0.0     # R_WRIST_YAW
    cmd.motor_cmd[28].kp = 330.0
    cmd.motor_cmd[28].kd = 1.0
    
    print("Starting BACK-BALANCED standing...")
    print("Pelvis: -0.10 rad BACK, Spine: 0.02 rad FORWARD")
    print("Center of mass shifted backward")
    print("Press Ctrl+C to stop")
    
    counter = 0
    try:
        while True:
            # Отправляем команду роботу
            pub.Write(cmd)
            
            # Выводим сообщение каждые 4 секунды
            if counter % 400 == 0:
                print(f"Back-balanced... {counter//100} seconds")
            
            counter += 1
            time.sleep(0.01)  # 100Hz контрольная частота
            
    except KeyboardInterrupt:
        print("\nBack-balanced standing stopped")
        
        # Плавное отключение - постепенно уменьшаем жесткость и демпфирование
        print("Smooth shutdown...")
        for step in range(120):
            for i in range(29):  # Для всех 29 основных моторов
                cmd.motor_cmd[i].kp *= 0.96  # Уменьшаем жесткость на 4% каждый шаг
                cmd.motor_cmd[i].kd *= 0.96  # Уменьшаем демпфирование на 4% каждый шаг
            pub.Write(cmd)  # Отправляем обновленную команду
            time.sleep(0.02)  # Небольшая пауза между шагами
        
        print("Shutdown complete")

if __name__ == '__main__':
    main()
