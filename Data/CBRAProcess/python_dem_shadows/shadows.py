import math

import numpy as np
import sys


def project_shadows_graphical(dem, sun_vector, dx, dy=None):
    peak = np.max(dem)
    v_x, v_y, v_z = sun_vector
    height_bin_x = v_z * dx / v_x
    height_bin_y = v_z * dy / v_y
    height_bin_x = int(np.round(height_bin_x, 2) * 10)
    height_bin_y = int(np.round(height_bin_y, 2) * 10)
    height_bin = float(math.gcd(height_bin_x, height_bin_y)) / 10
    if height_bin < 0.1:
        height_bin = 0.1

    if dy is None:
        dy = dx
    y_len, x_len = dem.shape
    x = np.arange(0, x_len)
    y = np.arange(0, y_len)
    X, Y = np.meshgrid(x, y)

    h = peak
    h_inverse = 0
    Z = np.copy(dem)

    x_distance_before = 0
    y_distance_before = 0
    shad = np.zeros_like(dem).astype(np.float32)

    while h > 0:
        h_inverse += height_bin
        h -= height_bin
        x_distance = np.round((v_x * h / v_z) / dx)
        y_distance = np.round((v_y * h / v_z) / dy)

        if abs(x_distance - x_distance_before) < 1 and abs(y_distance - y_distance_before) < 1:
            continue
        else:
            x_distance_before = x_distance
            y_distance_before = y_distance

        X_ = X[Z > h] - x_distance
        Y_ = Y[Z > h] - y_distance

        Z_gap = peak - Z[Z > h]
        Z_h_inverse = h_inverse - Z_gap

        mask = np.where((X_ >= 0) & (X_ < x_len) & (Y_ >= 0) & (Y_ < y_len), True, False)
        X_ALL = X_[mask].astype(np.int32)
        Y_ALL = Y_[mask].astype(np.int32)
        Z_ALL = Z_h_inverse[mask].astype(np.float32)
        shad_ = np.zeros_like(dem).astype(np.float32)
        shad_[Y_ALL, X_ALL] = Z_ALL

        shad = np.where(shad_ > shad, shad_, shad)

    shad = shad - height_bin

    shad[shad <= Z] = 0
    shad[shad != 0] = 1

    return shad


def project_shadows_graphical_v1(dem, sun_vector, dx, dy=None):
    peak = np.max(dem)
    v_x, v_y, v_z = sun_vector
    height_bin_x = v_z * dx / v_x
    height_bin_y = v_z * dy / v_y
    print(height_bin_x, height_bin_y)
    height_bin_x = int(np.round(height_bin_x, 2) * 10)
    height_bin_y = int(np.round(height_bin_y, 2) * 10)
    height_bin = float(math.gcd(height_bin_x, height_bin_y)) / 10
    if height_bin < 0.1:
        height_bin = 0.1
    # max_shadow_len = np.ceil(peak / altitude_tan)

    if dy is None:
        dy = dx
    y_len, x_len = dem.shape
    x = np.arange(0, x_len)
    y = np.arange(0, y_len)

    X, Y = np.meshgrid(x, y)

    h = peak
    h_inverse = 0
    Z = np.copy(dem)

    X_ALL = np.array([])
    Y_ALL = np.array([])
    Z_ALL = np.array([])
    x_distance_before = 0
    y_distance_before = 0
    shad = np.zeros_like(dem).astype(np.float32)

    print("height bin: ", height_bin)
    while h > 0:
        h_inverse += height_bin
        h -= height_bin
        x_distance = np.round((v_x * h / v_z) / dx)
        y_distance = np.round((v_y * h / v_z) / dy)

        if abs(x_distance - x_distance_before) < 1 and abs(y_distance - y_distance_before) < 1:
            continue
        else:
            print(h)
            x_distance_before = x_distance
            y_distance_before = y_distance

        X_ = X[Z > h] - x_distance
        Y_ = Y[Z > h] - y_distance

        Z_gap = peak - Z[Z > h]
        Z_h_inverse = h_inverse - Z_gap
        # Z_ = np.zeros_like(Y_) + h_inverse

        # X_building = X[Z > h]
        # Y_building = Y[Z > h]
        # Z_building = Z[Z > h]

        # X_ALL = np.hstack((X_ALL, X_))
        # Y_ALL = np.hstack((Y_ALL, Y_))
        # Z_ALL = np.hstack((Z_ALL, Z_h_inverse))
        #
        X_ALL = np.hstack((X_, X_ALL))
        Y_ALL = np.hstack((Y_, Y_ALL))
        Z_ALL = np.hstack((Z_h_inverse, Z_ALL))

    mask = np.where((X_ALL >= 0) & (X_ALL < x_len) & (Y_ALL >= 0) & (Y_ALL < y_len), True, False)
    X_ALL = X_ALL[mask].astype(np.int32)
    Y_ALL = Y_ALL[mask].astype(np.int32)
    Z_ALL = Z_ALL[mask].astype(np.float32)

    shad = np.zeros_like(dem).astype(np.float32)
    shad[Y_ALL, X_ALL] = Z_ALL

    shad[shad <= Z] = 0
    shad[shad != 0] = 1

    return shad


def project_shadows_graphical_v2(dem, sun_vector, dx, dy=None):
    peak = np.max(dem)
    v_x, v_y, v_z = sun_vector
    # v_xy = np.sqrt(v_x ** 2 + v_y ** 2)
    # altitude_tan = v_z / v_xy
    # azimuth_x = v_x / v_xy
    # azimuth_y = v_y / v_xy

    height_bin = 1
    height_min = np.min(dem)
    height_bin_x = v_z * dx / v_x
    height_bin_y = v_z * dy / v_y
    print(height_bin_x, height_bin_y)
    height_bin_x = int(np.round(height_bin_x, 2) * 10)
    height_bin_y = int(np.round(height_bin_y, 2) * 10)
    height_bin = float(math.gcd(height_bin_x, height_bin_y)) / 10
    # max_shadow_len = np.ceil(peak / altitude_tan)

    if dy is None:
        dy = dx
    y_len, x_len = dem.shape
    x = np.arange(0, x_len)
    y = np.arange(0, y_len)
    # y = y[0:y_len]
    # x = x[0:x_len]
    X, Y = np.meshgrid(x, y)

    h = peak
    # l_ = max_sha\dow_len
    h_inverse = 0
    Z = np.copy(dem)

    X_ALL = np.array([])
    Y_ALL = np.array([])
    Z_ALL = np.array([])
    x_distance_before = 0
    y_distance_before = 0
    h_last = 0
    print("height bin: ", height_bin)
    while h > 0:
        h_inverse += height_bin
        h -= height_bin
        # l_ = h_inverse / altitude_tan   # 单位是m
        # x_distance = np.round(l_ * azimuth_x / dx)
        x_distance = np.round((v_x * h_inverse / v_z) / dx)
        y_distance = np.round((v_y * h_inverse / v_z) / dy)
        if abs(x_distance - x_distance_before) < 1 and abs(y_distance - y_distance_before) < 1:
            continue
        else:
            # print(x_distance, y_distance)
            # print(h)
            x_distance_before = x_distance
            y_distance_before = y_distance
        # h_ = l_inverse * altitude_tan
        # mask = np.where(dem >= h, True, False)

        X_ = X[(Z <= h_inverse) & (Z > 0)] - x_distance
        Y_ = Y[(Z <= h_inverse) & (Z > 0)] - y_distance
        Z_ = np.zeros_like(Y_) + h_inverse

        # Z[Z <= h_inverse] = 0

        # X_building = X[Z > h]
        # Y_building = Y[Z > h]
        # Z_building = Z[Z > h]

        # X_ALL = np.hstack((X_ALL, X_))
        # Y_ALL = np.hstack((Y_ALL, Y_))
        # Z_ALL = np.hstack((Z_ALL, Z_))

        X_ALL = np.hstack((X_, X_ALL))
        Y_ALL = np.hstack((Y_, Y_ALL))
        Z_ALL = np.hstack((Z_, Z_ALL))
        # shadow_poses.append([X_, Y_, Z_])
        # X_[(X_ < 0) | (X_ > x_len * dx) | ()] = 1  # 被太阳照射到的地方

    Z_ALL = Z_ALL - height_bin
    mask = np.where((X_ALL >= 0) & (X_ALL < x_len) & (Y_ALL >= 0) & (Y_ALL < y_len), True, False)
    X_ALL = X_ALL[mask].astype(np.int32)
    Y_ALL = Y_ALL[mask].astype(np.int32)
    Z_ALL = Z_ALL[mask].astype(np.float32)
    #
    # X_ALL = X_ALL.astype(np.int32)
    # Y_ALL = Y_ALL.astype(np.int32)

    shad = np.zeros_like(dem).astype(np.float32)
    shad[Y_ALL, X_ALL] = Z_ALL
    # shad = np.where(Z != 0, Z, shad)
    # shad = np.where((Z >), 0)
    # shad[(Z != 0) & (shad > Z)] = 0
    shad[shad <= Z] = 0
    shad[shad != 0] = 1
    # shad[shad == 0] = np.nan
    # shad = shad[0: y_len, 0: x_len]
    return shad
    # shadow_height
    # position_xyz = np.concatenate((X, Y, dem), )


def project_shadows(dem, sun_vector, dx, dy=None):
    """Cast shadows on the DEM from a given sun position."""

    if dy is None:
        dy = dx

    inverse_sun_vector = _invert_sun_vector(sun_vector)
    normal_sun_vector = _normalize_sun_vector(sun_vector)

    rows, cols = dem.shape
    z = dem.T

    # Determine sun direction.
    if sun_vector[0] < 0:
        # The sun shines from the West.
        start_col = 1
    else:
        # THe sun shines from the East.
        start_col = cols - 1

    if sun_vector[1] < 0:
        # The sun shines from the North.
        start_row = 1
    else:
        # The sun shines from the South.
        start_row = rows - 1

    in_sun = np.ones_like(z)
    # Project West-East
    row = start_row
    for col in range(cols):
        _cast_shadow(row, col, rows, cols, dx, in_sun, inverse_sun_vector,
                     normal_sun_vector, z)

    # Project North-South
    col = start_col
    for row in range(rows):
        _cast_shadow(row, col, rows, cols, dy, in_sun, inverse_sun_vector,
                     normal_sun_vector, z)
    return in_sun.T


def _normalize_sun_vector(sun_vector):
    normal_sun_vector = np.zeros(3)
    normal_sun_vector[2] = np.sqrt(sun_vector[0] ** 2 + sun_vector[1] ** 2)
    normal_sun_vector[0] = -sun_vector[0] * sun_vector[2] / normal_sun_vector[2]
    normal_sun_vector[1] = -sun_vector[1] * sun_vector[2] / normal_sun_vector[2]
    return normal_sun_vector


def _invert_sun_vector(sun_vector):
    return -sun_vector / max(abs(sun_vector[:2]))


def _cast_shadow(row, col, rows, cols, dl, in_sun, inverse_sun_vector,
                 normal_sun_vector, z):
    n = 0
    z_previous = -sys.float_info.max
    """
    Uitleg Hans
    ------------
    Inverse sun vector staat je toe de projectie op projectievlak terug te rekenen
    naar de originele matrix.

    De dx en dy representeren tot hoever de schaduw rijkt vanaf de huidige cel.
    Normal sun vector is het vlak loodrecht op de richting van de zon.
    """

    while True:
        # Calculate projection offset
        dx = inverse_sun_vector[0] * n
        dy = inverse_sun_vector[1] * n
        col_dx = int(round(col + dx))
        row_dy = int(round(row + dy))
        if (col_dx < 0) or (col_dx >= cols) or (row_dy < 0) or (row_dy >= rows):
            break

        vector_to_origin = np.zeros(3)
        vector_to_origin[0] = dx * dl
        vector_to_origin[1] = dy * dl
        vector_to_origin[2] = z[col_dx, row_dy]
        z_projection = np.dot(vector_to_origin, normal_sun_vector)

        if z_projection < z_previous:
            in_sun[col_dx, row_dy] = 0
        else:
            z_previous = z_projection
        n += 1
