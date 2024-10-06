import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

output_dir = './static/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Borrar todos los archivos en el directorio ./static/
for file in os.listdir(output_dir):
    file_path = os.path.join(output_dir, file)
    if os.path.isfile(file_path):
        os.remove(file_path)

# Cargar el archivo CSV
cat_directory = './data/'
cat_file = cat_directory + 'XB.ELYSE.02.BHV.2022-01-02HR04_evid0006.csv'
# cat_file = cat_directory + 'XB.ELYSE.02.BHV.2022-02-03HR08_evid0005.csv'
cat = pd.read_csv(cat_file)

# Calculo de media y desviación estándar de la velocidad
mean_velocity = cat['velocity(m/s)'].mean()
std_velocity = cat['velocity(m/s)'].std()

# Definir límites
lower_limit = mean_velocity - 2 * std_velocity
upper_limit = mean_velocity + 2 * std_velocity

# Obtener la desviacion estandar de los datos dentro de los limites superiores e inferiores
std_threshold = cat[(cat['velocity(m/s)'] < upper_limit) & (cat['velocity(m/s)'] > lower_limit)]['velocity(m/s)'].std()

# Inicializar variables
start_index = None
start_time = None
end_time = None

# Lista para almacenar puntos de inicio, final y sus intervalos
anomalous_intervals = []
mid_points = []

# Definir tiempo de comparación
time_interval = 45

# Eliminar datos que se encuentren por dentro de los limites superiores e inferiores
new_data = cat[(cat['velocity(m/s)'] < lower_limit) | (cat['velocity(m/s)'] > upper_limit)]

for i in range(len(new_data)):
    # Verificar si el valor actual supera la media (nuevo punto de inicio)
    if new_data['velocity(m/s)'].iloc[i] > upper_limit:
        # Si es que el punto de inicio no esta siendo definido se toma el punto actual como punto de inicio
        if start_index is None:
            start_index = i
            start_time = new_data['time_rel(sec)'].iloc[i]
    
    # Una vez se asigna un punto de inicio verifica hasta donde tiene que llegar el intervalo
    if start_index is not None:
        # Aca se define el tiempo final del intervalo y no tiene final porque el time interval no reduce el tiempo
        end_time = start_time + time_interval
        # Crea un subset con los valores dentro del intervalo entre el tiempo inicial y el tiempo final
        subset = new_data[(new_data['time_rel(sec)'] > start_time) & (new_data['time_rel(sec)'] <= end_time)]
        subset_std = subset['velocity(m/s)'].std()

        # Si la desviacion estandar del subset es mayor a la desviacion estandar del threshold se considera un intervalo anómalo
        if subset_std > std_threshold:
            # Se añade el intervalo anómalo a la lista
            anomalous_intervals.append((start_time, end_time))
            start_index = None
            start_time = None
            end_time = None
        else:
            start_time = end_time

# Graficar los intervalos anómalos
plt.figure(figsize=(10, 6))

# Graficar todos los datos
plt.plot(new_data['time_rel(sec)'], new_data['velocity(m/s)'], label='Velocity over time', color='blue', marker='o')

# Graficar la media de la velocidad
plt.axhline(mean_velocity, color='green', linestyle='--', label='Mean Velocity')

# Resaltar intervalos anómalos
for start, end in anomalous_intervals:
    plt.axvspan(start, end, color='yellow', alpha=0.5, label='Anomalous Interval' if 'Anomalous Interval' not in plt.gca().get_legend_handles_labels()[1] else "")

# Añadir etiquetas y título
plt.title('Martian Seismic Activity: Anomalous Intervals with Start and End Points')
plt.xlabel('Time (seconds)')
plt.ylabel('Velocity (m/s)')
plt.legend()
plt.grid(True)

# Guardar el gráfico como imagen
output_path = os.path.join(output_dir, 'seismic_activity_anomalous_intervals_with_mean.png')
plt.savefig(output_path)


# Mostrar la gráfica
plt.show()
