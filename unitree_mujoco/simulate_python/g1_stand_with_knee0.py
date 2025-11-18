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
    # НОГИ: Таз ОТВЕДЕН НАЗАД для баланса против веса головы и рук
    # ==========================================================================
    
    # Левая нога - таз сильно назад для смещения центра масс
    cmd.motor_cmd[0].q = -0.75   # L_HIP_PITCH - Таз бедро вперед/назад: отрицательное = отклонение НАЗАД
    cmd.motor_cmd[0].kp = 300.0   # Жесткость удержания позиции таза (stiffness for hip pitch)
    cmd.motor_cmd[0].kd = 3.0    # Демпфирование колебаний таза (damping for hip pitch)
    
    cmd.motor_cmd[1].q = 0.15     # L_HIP_ROLL - Таз бедро вбок: 0 = нейтральное положение
    cmd.motor_cmd[1].kp = 300.0   # Жесткость удержания позиции бедра вбок
    cmd.motor_cmd[1].kd = 3.0    # Демпфирование колебаний бедра вбок
    
    cmd.motor_cmd[2].q = 0.10     # L_HIP_YAW - Таз бедро вращение: 0 = нейтральное положение
    cmd.motor_cmd[2].kp = 300.0   # Жесткость удержания позиции вращения бедра
    cmd.motor_cmd[2].kd = 2.0    # Демпфирование колебаний вращения бедра
    
    cmd.motor_cmd[3].q = 0.60    # L_KNEE - Колено: положительное = СГИБ, отрицательное = разгиб
    cmd.motor_cmd[3].kp = 300.0  # Высокая жесткость для колена - основная опора
    cmd.motor_cmd[3].kd = 4.0    # Сильное демпфирование для колена
    
    cmd.motor_cmd[4].q = -0.10    # L_ANKLE_PITCH - Голеностоп вперед/назад: положительное = пятка вниз
    cmd.motor_cmd[4].kp = 400.0   # Жесткость голеностопа
    cmd.motor_cmd[4].kd = 3.0    # Демпфирование голеностопа
    
    cmd.motor_cmd[5].q = -0.18     # L_ANKLE_ROLL - Голеностоп вбок: 0 = нейтральное положение
    cmd.motor_cmd[5].kp = 400.0   # Жесткость голеностопа вбок
    cmd.motor_cmd[5].kd = 3.0    # Демпфирование голеностопа вбок
#////////////////////////////////////////////////////////////////////////////////////////    
    # Правая нога - симметрично левой
    cmd.motor_cmd[6].q = -0.75   # R_HIP_PITCH - Таз бедро вперед/назад: отрицательное = отклонение НАЗАД
    cmd.motor_cmd[6].kp = 300.0   # Жесткость удержания позиции таза
    cmd.motor_cmd[6].kd = 3.0    # Демпфирование колебаний таза
    
    cmd.motor_cmd[7].q = -0.15     # R_HIP_ROLL - Таз бедро вбок: 0 = нейтральное положение
    cmd.motor_cmd[7].kp = 300.0   # Жесткость удержания позиции бедра вбок
    cmd.motor_cmd[7].kd = 3.0    # Демпфирование колебаний бедра вбок
    
    cmd.motor_cmd[8].q = 0.10     # R_HIP_YAW - Таз бедро вращение: 0 = нейтральное положение
    cmd.motor_cmd[8].kp = 300.0   # Жесткость удержания позиции вращения бедра
    cmd.motor_cmd[8].kd = 2.0    # Демпфирование колебаний вращения бедра
    
    cmd.motor_cmd[9].q = 0.60    # R_KNEE - Колено: положительное = СГИБ, отрицательное = разгиб
    cmd.motor_cmd[9].kp = 300.0  # Высокая жесткость для колена - основная опора
    cmd.motor_cmd[9].kd = 4.0    # Сильное демпфирование для колена
    
    cmd.motor_cmd[10].q = -0.10   # R_ANKLE_PITCH - Голеностоп вперед/назад: положительное = пятка вниз
    cmd.motor_cmd[10].kp = 400.0  # Жесткость голеностопа
    cmd.motor_cmd[10].kd = 3.0   # Демпфирование голеностопа
    
    cmd.motor_cmd[11].q = 0.18    # R_ANKLE_ROLL - Голеностоп вбок: 0 = нейтральное положение
    cmd.motor_cmd[11].kp = 400.0  # Жесткость голеностопа вбок
    cmd.motor_cmd[11].kd = 3.0   # Демпфирование голеностопа вбок
    
    # ==========================================================================
    # ТАЗ И СПИНА: ОТКЛОНЕНЫ НАЗАД для противовеса
    # ==========================================================================
    
    cmd.motor_cmd[12].q = 0.0    # WAIST_YAW - Талия вращение: 0 = прямо
    cmd.motor_cmd[12].kp = 300.0  # Жесткость талии вращение
    cmd.motor_cmd[12].kd = 2.5   # Демпфирование талии вращение
    
    cmd.motor_cmd[13].q = 0.0    # WAIST_ROLL - Талия наклон вбок: 0 = прямо
    cmd.motor_cmd[13].kp = 300.0  # Жесткость талии наклон вбок
    cmd.motor_cmd[13].kd = 2.5   # Демпфирование талии наклон вбок
    
    cmd.motor_cmd[14].q = 0.25   # WAIST_PITCH - Талия наклон вперед/назад: положительное = ВПЕРЕд
    cmd.motor_cmd[14].kp = 300.0  # Жесткость талии наклон вперед/назад
    cmd.motor_cmd[14].kd = 2.5   # Демпфирование талии наклон вперед/назад
    
    # ==========================================================================
    # РУКИ: скомпенсированы назад для баланса
    # ==========================================================================
    
    # Левая рука - немного назад для компенсации веса
    cmd.motor_cmd[15].q = -0.25  # L_SHOULDER_PITCH - Плечо вперед/назад: отрицательное = НАЗАД
    cmd.motor_cmd[15].kp = 300.0  # Жесткость плеча вперед/назад
    cmd.motor_cmd[15].kd = 2.0   # Демпфирование плеча вперед/назад
    
    cmd.motor_cmd[16].q = 0.23    # L_SHOULDER_ROLL - Плечо вверх/вниз: 0 = нейтральное
    cmd.motor_cmd[16].kp = 300.0  # Жесткость плеча вверх/вниз
    cmd.motor_cmd[16].kd = 2.0   # Демпфирование плеча вверх/вниз
    
    cmd.motor_cmd[17].q = 0.0    # L_SHOULDER_YAW - Плечо вращение: 0 = нейтральное
    cmd.motor_cmd[17].kp = 300.0  # Жесткость плеча вращение
    cmd.motor_cmd[17].kd = 1.5   # Демпфирование плеча вращение
    
    cmd.motor_cmd[18].q = 0.7   # L_ELBOW - Локоть: отрицательное = СГИБ
    cmd.motor_cmd[18].kp = 300.0  # Жесткость локтя
    cmd.motor_cmd[18].kd = 2.0   # Демпфирование локтя
    
    cmd.motor_cmd[19].q = 0.0    # L_WRIST_ROLL - Запястье вращение: 0 = нейтральное
    cmd.motor_cmd[19].kp = 300.0  # Жесткость запястья вращение
    cmd.motor_cmd[19].kd = 1.0   # Демпфирование запястья вращение
    
    cmd.motor_cmd[20].q = 0.0    # L_WRIST_PITCH - Запястье вперед/назад: 0 = нейтральное
    cmd.motor_cmd[20].kp = 300.0  # Жесткость запястья вперед/назад
    cmd.motor_cmd[20].kd = 1.0   # Демпфирование запястья вперед/назад
    
    cmd.motor_cmd[21].q = 0.0    # L_WRIST_YAW - Запястье вбок: 0 = нейтральное
    cmd.motor_cmd[21].kp = 300.0  # Жесткость запястья вбок
    cmd.motor_cmd[21].kd = 1.0   # Демпфирование запястья вбок
    
    # Правая рука - симметрично левой
    cmd.motor_cmd[22].q = -0.25  # R_SHOULDER_PITCH - Плечо вперед/назад: отрицательное = НАЗАД
    cmd.motor_cmd[22].kp = 300.0  # Жесткость плеча вперед/назад
    cmd.motor_cmd[22].kd = 2.0   # Демпфирование плеча вперед/назад
    
    cmd.motor_cmd[23].q = -0.23    # R_SHOULDER_ROLL - Плечо вверх/вниз: 0 = нейтральное
    cmd.motor_cmd[23].kp = 300.0  # Жесткость плеча вверх/вниз
    cmd.motor_cmd[23].kd = 2.0   # Демпфирование плеча вверх/вниз
    
    cmd.motor_cmd[24].q = 0.0    # R_SHOULDER_YAW - Плечо вращение: 0 = нейтральное
    cmd.motor_cmd[24].kp = 300.0  # Жесткость плеча вращение
    cmd.motor_cmd[24].kd = 1.5   # Демпфирование плеча вращение
    
    cmd.motor_cmd[25].q = 0.7   # R_ELBOW - Локоть: отрицательное = СГИБ
    cmd.motor_cmd[25].kp = 300.0  # Жесткость локтя
    cmd.motor_cmd[25].kd = 2.0   # Демпфирование локтя
    
    cmd.motor_cmd[26].q = 0.0    # R_WRIST_ROLL - Запястье вращение: 0 = нейтральное
    cmd.motor_cmd[26].kp = 300.0  # Жесткость запястья вращение
    cmd.motor_cmd[26].kd = 1.0   # Демпфирование запястья вращение
    
    cmd.motor_cmd[27].q = 0.0    # R_WRIST_PITCH - Запястье вперед/назад: 0 = нейтральное
    cmd.motor_cmd[27].kp = 300.0  # Жесткость запястья вперед/назад
    cmd.motor_cmd[27].kd = 1.0   # Демпфирование запястья вперед/назад
    
    cmd.motor_cmd[28].q = 0.0    # R_WRIST_YAW - Запястье вбок: 0 = нейтральное
    cmd.motor_cmd[28].kp = 300.0  # Жесткость запястья вбок
    cmd.motor_cmd[28].kd = 1.0   # Демпфирование запястья вбок
    
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
