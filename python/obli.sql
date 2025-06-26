-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS empleados;

-- Usar la base de datos creada
USE empleados;

-- Crear la tabla para almacenar los datos
CREATE TABLE IF NOT EXISTS empleados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    puesto VARCHAR(100),
    salario DECIMAL(10, 2)
);

-- Insertar datos de ejemplo
INSERT INTO empleados (nombre, puesto, salario)
VALUES
    ('Juan Pérez', 'Desarrollador', 3000.00),
    ('Ana García', 'Gerente', 4500.00),
    ('Luis Rodríguez', 'Analista', 3500.00),
    ('María López', 'Diseñadora', 2800.00),
    ('Carlos Sánchez', 'Jefe de equipo', 5000.00),
    ('Laura Fernández', 'Tester', 2200.00),
    ('Pedro Martínez', 'Administrador de bases de datos', 3700.00),
    ('Marta Gómez', 'Soporte técnico', 2500.00),
    ('José Ramírez', 'Consultor', 4200.00),
    ('Isabel Torres', 'Community Manager', 3100.00),
    ('Andrés Díaz', 'Marketing', 3400.00),
    ('Beatriz Pérez', 'Recursos Humanos', 3100.00),
    ('Francisco Castro', 'Desarrollador Backend', 3800.00),
    ('Carmen Ruiz', 'Diseñadora UI/UX', 2900.00),
    ('Raúl Fernández', 'Administrador de sistemas', 3600.00),
    ('Susana López', 'Jefe de ventas', 4800.00),
    ('David González', 'Operaciones', 2700.00),
    ('Patricia García', 'Consultora estratégica', 4600.00),
    ('Fernando Martínez', 'CEO', 8000.00),
    ('Alba Pérez', 'Asistente administrativo', 2300.00),
    ('Javier Romero', 'Contador', 3300.00),
    ('Sonia Castillo', 'Desarrolladora Frontend', 3100.00),
    ('Victor Hernández', 'Project Manager', 4400.00),
    ('Marina Soto', 'Analista de datos', 3200.00),
    ('Ricardo Jiménez', 'Técnico de redes', 2600.00),
    ('Julia Martínez', 'Diseñadora Gráfica', 2800.00),
    ('Oscar Sánchez', 'Vendedor', 2200.00),
    ('Eva Rodríguez', 'Administración', 2400.00),
    ('Marcelo Pérez', 'Director de Tecnología', 5500.00);
