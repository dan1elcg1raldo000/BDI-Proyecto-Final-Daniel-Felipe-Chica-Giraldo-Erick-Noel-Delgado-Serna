PRAGMA foreign_keys = ON;
BEGIN;
CREATE TABLE fuente (
 id INTEGER PRIMARY KEY,
 hoja TEXT NOT NULL UNIQUE,
 archivo_sha256 TEXT CHECK(archivo_sha256 IS NULL OR length(archivo_sha256)=64),
 ambito TEXT NOT NULL CHECK(ambito IN ('PRINCIPAL','AUXILIAR','DEMO'))
);
CREATE TABLE maquina (
 id INTEGER PRIMARY KEY,
 nombre TEXT NOT NULL UNIQUE CHECK(length(nombre) BETWEEN 1 AND 30),
 activa INTEGER NOT NULL DEFAULT 1 CHECK(activa IN (0,1))
);
CREATE TABLE turno (
 id INTEGER PRIMARY KEY,
 nombre TEXT NOT NULL UNIQUE CHECK(length(nombre) BETWEEN 1 AND 40),
 inicio TEXT NOT NULL CHECK(length(inicio)=5 AND inicio GLOB '[0-2][0-9]:[0-5][0-9]' AND inicio<'24:00'),
 fin TEXT NOT NULL CHECK(length(fin)=5 AND fin GLOB '[0-2][0-9]:[0-5][0-9]' AND fin<'24:00')
);
CREATE TABLE persona (
 id INTEGER PRIMARY KEY,
 seudonimo TEXT NOT NULL UNIQUE CHECK(length(seudonimo) BETWEEN 1 AND 30),
 activa INTEGER NOT NULL DEFAULT 1 CHECK(activa IN (0,1))
);
CREATE TABLE referencia (
 id INTEGER PRIMARY KEY,
 nombre TEXT NOT NULL UNIQUE CHECK(length(nombre) BETWEEN 1 AND 120)
);
CREATE TABLE codigo_paro (
 codigo TEXT PRIMARY KEY NOT NULL CHECK(length(codigo)=2 AND codigo GLOB '[0-9][0-9]'),
 descripcion TEXT NOT NULL CHECK(length(descripcion) BETWEEN 1 AND 180)
);
CREATE TABLE subcodigo_paro (
 codigo TEXT NOT NULL REFERENCES codigo_paro(codigo) ON DELETE RESTRICT ON UPDATE CASCADE,
 subcodigo TEXT NOT NULL CHECK(length(subcodigo) BETWEEN 1 AND 15),
 descripcion TEXT NOT NULL CHECK(length(descripcion) BETWEEN 1 AND 180),
 PRIMARY KEY(codigo,subcodigo)
);
-- Grano histórico: una fila de origen, principal o detalle, sin propagar cantidades.
-- La captura nueva exige tiempo, referencia, turno y producción conocidos.
CREATE TABLE registro_produccion (
 id INTEGER PRIMARY KEY,
 fecha TEXT NOT NULL CHECK(length(fecha)=10 AND fecha GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]' AND date(fecha,'+0 days') IS NOT NULL AND date(fecha,'+0 days')=fecha),
 maquina_id INTEGER NOT NULL REFERENCES maquina(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 turno_id INTEGER REFERENCES turno(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 operario_id INTEGER REFERENCES persona(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 referencia_id INTEGER REFERENCES referencia(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 minutos_base REAL CHECK(minutos_base IS NULL OR minutos_base BETWEEN 0 AND 1440),
 meta_pacas_hora REAL CHECK(meta_pacas_hora IS NULL OR meta_pacas_hora>0),
 pacas_reales REAL DEFAULT 0 CHECK(pacas_reales IS NULL OR pacas_reales>=0),
 origen TEXT NOT NULL UNIQUE CHECK(length(origen) BETWEEN 1 AND 160),
 clase TEXT NOT NULL DEFAULT 'REAL' CHECK(clase IN ('REAL','DEMO')),
 creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 fuente_id INTEGER NOT NULL DEFAULT 4 REFERENCES fuente(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 fila_fuente INTEGER CHECK(fila_fuente IS NULL OR fila_fuente>0),
 estado TEXT NOT NULL DEFAULT 'CAPTURA' CHECK(estado IN ('CAPTURA','HISTORICO')),
 minutos_sin_trabajar REAL CHECK(minutos_sin_trabajar IS NULL OR minutos_sin_trabajar>=0),
 UNIQUE(fuente_id,fila_fuente),
 CHECK(estado='HISTORICO' OR (minutos_base>0 AND minutos_base IS NOT NULL AND pacas_reales IS NOT NULL AND turno_id IS NOT NULL AND referencia_id IS NOT NULL))
);
-- Grano: duración atribuida a una causa/subcausa dentro del segmento. No equivale
-- a un evento individual: el formato histórico no garantiza hora de inicio/fin.
CREATE TABLE paro (
 id INTEGER PRIMARY KEY,
 registro_id INTEGER NOT NULL REFERENCES registro_produccion(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 codigo TEXT NOT NULL REFERENCES codigo_paro(codigo) ON DELETE RESTRICT ON UPDATE CASCADE,
 subcodigo TEXT,
 minutos REAL NOT NULL CHECK(minutos>0),
 observacion TEXT CHECK(observacion IS NULL OR length(observacion)<=500),
 agente TEXT CHECK(agente IS NULL OR length(agente)<=60),
 FOREIGN KEY(codigo,subcodigo) REFERENCES subcodigo_paro(codigo,subcodigo) ON DELETE RESTRICT ON UPDATE CASCADE
);
CREATE TABLE intervencion (
 paro_id INTEGER NOT NULL REFERENCES paro(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 persona_id INTEGER NOT NULL REFERENCES persona(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 rol TEXT NOT NULL CHECK(rol IN ('MANTENIMIENTO','OPERACION','CALIDAD','OTRO')),
 PRIMARY KEY(paro_id,persona_id)
);
CREATE TABLE produccion_hora (
 registro_id INTEGER NOT NULL REFERENCES registro_produccion(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 hora_relativa INTEGER NOT NULL CHECK(typeof(hora_relativa)='integer' AND hora_relativa BETWEEN 0 AND 23),
 pacas REAL NOT NULL CHECK(pacas>=0),
 PRIMARY KEY(registro_id,hora_relativa)
);
-- Trazabilidad de la extracción PDF previa; no alimenta los indicadores del XLSM.
CREATE TABLE staging_pdf (
 id INTEGER PRIMARY KEY,
 pagina INTEGER NOT NULL CHECK(pagina BETWEEN 1 AND 3213),
 linea INTEGER NOT NULL CHECK(linea>0),
 fecha TEXT NOT NULL,
 maquina TEXT NOT NULL,
 estado TEXT NOT NULL DEFAULT 'PENDIENTE_EXCEL' CHECK(estado IN ('PENDIENTE_EXCEL','REVISADO')),
 UNIQUE(pagina,linea)
);
CREATE INDEX idx_registro_maquina_fecha ON registro_produccion(maquina_id,fecha);
CREATE INDEX idx_registro_fecha_turno ON registro_produccion(fecha,turno_id);
CREATE INDEX idx_paro_registro_codigo ON paro(registro_id,codigo);
CREATE INDEX idx_paro_subcodigo ON paro(codigo,subcodigo);
CREATE INDEX idx_registro_referencia ON registro_produccion(referencia_id);
CREATE INDEX idx_registro_operario ON registro_produccion(operario_id);
CREATE INDEX idx_intervencion_persona ON intervencion(persona_id);
CREATE TRIGGER codigo_18_nueva_captura BEFORE INSERT ON paro
WHEN NEW.codigo='18' AND (SELECT estado FROM registro_produccion WHERE id=NEW.registro_id)='CAPTURA'
BEGIN SELECT RAISE(ABORT,'Código 18 pendiente de aprobación para nuevas capturas'); END;
CREATE TRIGGER codigo_18_modificacion_captura BEFORE UPDATE OF codigo,registro_id ON paro
WHEN NEW.codigo='18' AND (SELECT estado FROM registro_produccion WHERE id=NEW.registro_id)='CAPTURA'
BEGIN SELECT RAISE(ABORT,'Código 18 pendiente de aprobación para nuevas capturas'); END;
CREATE TRIGGER validar_paro_insert BEFORE INSERT ON paro
WHEN (SELECT estado FROM registro_produccion WHERE id=NEW.registro_id)='CAPTURA' AND NEW.minutos+COALESCE((SELECT SUM(minutos) FROM paro WHERE registro_id=NEW.registro_id),0)
 > (SELECT minutos_base FROM registro_produccion WHERE id=NEW.registro_id)
BEGIN SELECT RAISE(ABORT,'Los paros superan los minutos programados'); END;
CREATE TRIGGER validar_paro_update BEFORE UPDATE OF minutos,registro_id ON paro
WHEN (SELECT estado FROM registro_produccion WHERE id=NEW.registro_id)='CAPTURA' AND NEW.minutos+COALESCE((SELECT SUM(minutos) FROM paro WHERE registro_id=NEW.registro_id AND id<>OLD.id),0)
 > (SELECT minutos_base FROM registro_produccion WHERE id=NEW.registro_id)
BEGIN SELECT RAISE(ABORT,'Los paros superan los minutos programados'); END;
CREATE TRIGGER validar_registro_update BEFORE UPDATE OF minutos_base,pacas_reales,estado ON registro_produccion
WHEN NEW.estado='CAPTURA' AND (NEW.minutos_base<COALESCE((SELECT SUM(minutos) FROM paro WHERE registro_id=OLD.id),0)
 OR NEW.pacas_reales<COALESCE((SELECT SUM(pacas) FROM produccion_hora WHERE registro_id=OLD.id),0)
 OR EXISTS(SELECT 1 FROM produccion_hora WHERE registro_id=OLD.id AND hora_relativa*60>=NEW.minutos_base))
BEGIN SELECT RAISE(ABORT,'El segmento es menor que su detalle'); END;
CREATE TRIGGER validar_hora_insert BEFORE INSERT ON produccion_hora
WHEN NEW.pacas+COALESCE((SELECT SUM(pacas) FROM produccion_hora WHERE registro_id=NEW.registro_id),0)
 > (SELECT pacas_reales FROM registro_produccion WHERE id=NEW.registro_id)
 OR NEW.hora_relativa*60 >= (SELECT minutos_base FROM registro_produccion WHERE id=NEW.registro_id)
BEGIN SELECT RAISE(ABORT,'Detalle horario fuera del segmento'); END;
CREATE TRIGGER validar_hora_update BEFORE UPDATE ON produccion_hora
WHEN NEW.pacas+COALESCE((SELECT SUM(pacas) FROM produccion_hora WHERE registro_id=NEW.registro_id AND NOT(registro_id=OLD.registro_id AND hora_relativa=OLD.hora_relativa)),0)
 > (SELECT pacas_reales FROM registro_produccion WHERE id=NEW.registro_id)
 OR NEW.hora_relativa*60 >= (SELECT minutos_base FROM registro_produccion WHERE id=NEW.registro_id)
BEGIN SELECT RAISE(ABORT,'Detalle horario fuera del segmento'); END;

CREATE TABLE staging_xlsm (
 fuente_id INTEGER NOT NULL REFERENCES fuente(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 fila INTEGER NOT NULL CHECK(fila>0),
 contenido_json TEXT NOT NULL CHECK(json_valid(contenido_json)),
 PRIMARY KEY(fuente_id,fila)
);
CREATE TABLE incidencia (
 id INTEGER PRIMARY KEY,
 registro_id INTEGER REFERENCES registro_produccion(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 fuente_id INTEGER NOT NULL REFERENCES fuente(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 fila INTEGER NOT NULL,
 tipo TEXT NOT NULL,
 detalle TEXT NOT NULL,
 FOREIGN KEY(fuente_id,fila) REFERENCES staging_xlsm(fuente_id,fila) ON DELETE RESTRICT ON UPDATE CASCADE
);
CREATE INDEX idx_registro_fuente ON registro_produccion(fuente_id,fila_fuente);
CREATE INDEX idx_incidencia_registro ON incidencia(registro_id);

COMMIT;
