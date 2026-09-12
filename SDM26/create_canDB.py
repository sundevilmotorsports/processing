import cantools

def create_signal(name, start, length, is_signed, scale=1.0, offset=0.0, unit="", 
                  is_multiplexer=False, multiplexer_ids=None, multiplexer_signal=None):
    """
    Bulletproof wrapper to create signals, dynamically supporting multiple cantools versions
    and handling Multiplexed (overlapping) ECU messages.
    """
    kwargs = {
        'name': name, 'start': start, 'length': length, 
        'byte_order': 'little_endian', 'is_signed': is_signed, 'unit': unit,
        'is_multiplexer': is_multiplexer, 
        'multiplexer_ids': multiplexer_ids,
        'multiplexer_signal': multiplexer_signal
    }

    # Attempt 1: Modern cantools (using BaseConversion)
    try:
        from cantools.database.conversion import BaseConversion
        kwargs['conversion'] = BaseConversion.factory(scale=scale, offset=offset)
        return cantools.database.can.Signal(**kwargs)
    except Exception:
        pass
        
    # Attempt 2: Mid-generation cantools (using LinearConversion)
    try:
        from cantools.database.can.conversion import LinearConversion
        kwargs['conversion'] = LinearConversion(scale, offset)
        return cantools.database.can.Signal(**kwargs)
    except Exception:
        pass

    # Attempt 3: Legacy cantools (direct kwargs)
    kwargs['scale'] = scale
    kwargs['offset'] = offset
    return cantools.database.can.Signal(**kwargs)


def generate_full_dbc(output_filename="SDM26_Generated.dbc"):
    db = cantools.database.Database()
    messages = []

    # ==========================================
    # 1. IMU MESSAGES (Shifted by / 1000)
    # ==========================================
    # Scale: 0.122 / 1000 = 0.000122
    sig_imu_accel = [
        create_signal('IMU_ACCEL_X', 0, 16, True, 0.000122, 0, "G"),
        create_signal('IMU_ACCEL_Y', 16, 16, True, 0.000122, 0, "G"),
        create_signal('IMU_ACCEL_Z', 32, 16, True, 0.000122, 0, "G")
    ]
    messages.append(cantools.database.can.Message(865, 'IMU_ACCEL', 8, sig_imu_accel))

    sig_imu_gyro = [
        create_signal('IMU_GYRO_X', 0, 16, True, 17.5, 0, "mdps"),
        create_signal('IMU_GYRO_Y', 16, 16, True, 17.5, 0, "mdps"),
        create_signal('IMU_GYRO_Z', 32, 16, True, 17.5, 0, "mdps")
    ]
    messages.append(cantools.database.can.Message(864, 'IMU_GYRO', 8, sig_imu_gyro))


    # ==========================================
    # 2. WHEEL BOARDS (Temps shifted by / 1000)
    # ==========================================
    # Math: ((v * 0.02) - 273.15) / 1000 
    # Scale: 0.02 / 1000 = 0.00002
    # Offset: -273.15 / 1000 = -0.27315
    def get_wheel_signals(prefix):
        return [
            create_signal(f'{prefix}_rpm', 0, 16, False, 1, 0, "rpm"),
            create_signal(f'{prefix}_ObjTemp', 16, 16, False, 0.00002, -0.27315, "kC"),
            create_signal(f'{prefix}_AmbTemp', 32, 16, False, 0.00002, -0.27315, "kC")
        ]
    messages.append(cantools.database.can.Message(867, 'FLWB', 8, get_wheel_signals('FLWB')))
    messages.append(cantools.database.can.Message(868, 'FRWB', 8, get_wheel_signals('FRWB')))
    messages.append(cantools.database.can.Message(869, 'RRWB', 8, get_wheel_signals('RRWB')))
    messages.append(cantools.database.can.Message(870, 'RLWB', 8, get_wheel_signals('RLWB')))


    # ==========================================
    # 3. STRAIN GAUGES (Massive offsets included)
    # ==========================================
    messages.append(cantools.database.can.Message(1250, 'FLSG', 8, [
        create_signal('FLSG_Strain', 0, 16, False, -11052026.1, 2606.22253)
    ]))
    
    messages.append(cantools.database.can.Message(1251, 'FRSG', 8, [
        create_signal('FRSG_Strain', 0, 16, True, 1.0, 0.0)
    ]))
    
    messages.append(cantools.database.can.Message(1252, 'RRSG', 8, [
        create_signal('RRSG_Strain', 0, 16, True, 1.0, 0.0)
    ]))
    
    messages.append(cantools.database.can.Message(1253, 'RLSG', 8, [
        create_signal('RLSG_Strain', 0, 16, True, -1401922.44, 92026.0137)
    ]))


    # ==========================================
    # 4. ENGINE (MULTIPLEXED) & SHIFTER 
    # ==========================================
    sig_engine = [
        create_signal('ENGINE_Mux', 0, 8, False, is_multiplexer=True),
        create_signal('ENGINE_Speed', 8, 16, False, multiplexer_ids=[0], multiplexer_signal='ENGINE_Mux'),
        create_signal('ENGINE_ect', 24, 8, True, multiplexer_ids=[0], multiplexer_signal='ENGINE_Mux'),
        create_signal('ENGINE_OilTemp', 32, 8, True, multiplexer_ids=[0], multiplexer_signal='ENGINE_Mux'),
        create_signal('ENGINE_OilPressure', 40, 16, True, multiplexer_ids=[0], multiplexer_signal='ENGINE_Mux'),
        create_signal('ENGINE_tps', 16, 8, True, multiplexer_ids=[1], multiplexer_signal='ENGINE_Mux'),
        create_signal('ENGINE_Driven_wspd', 32, 16, False, multiplexer_ids=[1], multiplexer_signal='ENGINE_Mux'),
        create_signal('ENGINE_aps', 8, 8, True, multiplexer_ids=[2], multiplexer_signal='ENGINE_Mux')
    ]
    messages.append(cantools.database.can.Message(1000, 'ENGINE', 8, sig_engine))

    sig_shifter = [
        create_signal('SHIFTER_Shift0', 0, 8, True),
        create_signal('SHIFTER_Shift1', 8, 8, True),
        create_signal('SHIFTER_Shift2', 16, 8, True)
    ]
    messages.append(cantools.database.can.Message(64, 'SHIFTER', 8, sig_shifter))


    # ==========================================
    # 5. NEW: STEERING & SHOCKS
    # ==========================================
    sig_steering = [
        create_signal('STEERING', 0, 16, False, 0.084769, -152.846451, "deg")
    ]
    messages.append(cantools.database.can.Message(900, 'STEERING_DATA', 8, sig_steering))

    sig_shocks = [
        create_signal('FLSHOCK', 0, 16, False, -0.018586, 76.399026, "mm"),
        create_signal('FRSHOCK', 16, 16, False, -0.018444, 75.894221, "mm"),
        create_signal('RLSHOCK', 32, 16, False, -0.018600, 76.618397, "mm"),
        create_signal('RRSHOCK', 48, 16, False, -0.018498, 76.591013, "mm")
    ]
    messages.append(cantools.database.can.Message(901, 'SHOCK_DATA', 8, sig_shocks))

    # Add everything to the database object and save
    db.messages.extend(messages)
    
    with open(output_filename, "w") as f:
        f.write(db.as_dbc_string())

    print("DBC created")

# Run it
generate_full_dbc("SDM26_Generated.dbc")