-- Base de Datos

-- Creación de base de datos TAIS_DM
CREATE DATABASE [TAIS_DM];

-- Selección de base de datos TAIS_DM
USE [TAIS_DM];

-- Tablas de Dimensiones

-- Creación de tabla de dimensión de Criterios de Aceptación
CREATE TABLE [dimCriterios] (
  [idCriterio] SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [Criterio]   NVARCHAR(40)    NOT NULL,
     PRIMARY KEY ( [idCriterio] ));

-- Creación de tabla de dimensión de Grupos Etarios
CREATE TABLE [dimEtarios] (
  [idEtario] SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [Etario]   NVARCHAR(40)    NOT NULL,
     PRIMARY KEY ( [idEtario] ));

-- Creación de tabla de dimensión de Factores
CREATE TABLE [dimFactores] (
  [IdFactor] SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [Factor]   NVARCHAR(40)    NOT NULL,
     PRIMARY KEY ( [IdFactor] ));

-- Creación de tabla de dimensión de Familias de Beneficiarios
CREATE TABLE [dimFamilias] (
  [idFamilia]   INT    NOT NULL    IDENTITY ( 1 , 1 ),
  [idLocalidad] SMALLINT    NOT NULL,
     PRIMARY KEY ( [idFamilia] ));
CREATE NONCLUSTERED INDEX [IDIMFAMILIAS1] ON [dimFamilias] (
      [idLocalidad]);
ALTER TABLE [dimFamilias]
 ADD CONSTRAINT [IDIMFAMILIAS1] FOREIGN KEY ( [idLocalidad] ) REFERENCES [dimLocalidades]([idLocalidad]);

-- Creación de tabla de dimensión de Fechas
CREATE TABLE [dimFechas] (
  [IdFecha]      SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [Periodo] INT    NOT NULL,
  [Fecha]   DATETIME    NOT NULL,
     PRIMARY KEY ( [IdFecha] ));

-- Creación de tabla de dimensión de Localidades
CREATE TABLE [dimLocalidades] (
  [idLocalidad] SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [Localidad]   NVARCHAR(40)    NOT NULL,
     PRIMARY KEY ( [idLocalidad] ));

-- Creación de tabla de dimensión de Municipios
CREATE TABLE [dimMunicipios] (
  [IdMunicipio] SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [Municipio]   NVARCHAR(40)    NOT NULL,
     PRIMARY KEY ( [IdMunicipio] ));

-- Creación de tabla de dimensión de Novedades
CREATE TABLE [dimNovedades] (
  [IdNovedad]      INT    NOT NULL    IDENTITY ( 1 , 1 ),
  [Tipo]    NCHAR(3)    NOT NULL,
  [IdPersona]      SMALLINT    NOT NULL,
  [Periodo] INT    NOT NULL,
  [Activo]  BIT    NOT NULL,
  [IdMunicipio]    SMALLINT    NOT NULL,
     PRIMARY KEY ( [IdNovedad] ));
CREATE NONCLUSTERED INDEX [IDIMNOVEDADES1] ON [dimNovedades] (
      [IdMunicipio]);
CREATE NONCLUSTERED INDEX [IDIMNOVEDADES2] ON [dimNovedades] (
      [IdPersona]);
ALTER TABLE [dimNovedades]
 ADD CONSTRAINT [IDIMNOVEDADES2] FOREIGN KEY ( [IdPersona] ) REFERENCES [dimPersonas]([IdPersona]);
ALTER TABLE [dimNovedades]
 ADD CONSTRAINT [IDIMNOVEDADES1] FOREIGN KEY ( [IdMunicipio] ) REFERENCES [dimMunicipios]([IdMunicipio]);

-- Creación de tabla de dimensión de Movimientos Operativos
CREATE TABLE [dimOperativos] (
  [IdOperativo]     INT    NOT NULL    IDENTITY ( 1 , 1 ),
  [Fecha]  DATETIME    NOT NULL,
  [Monto]  MONEY    NOT NULL,
  [Activo] BIT    NOT NULL,
     PRIMARY KEY ( [IdOperativo] ));

-- Creación de tabla de dimensión de Padrones de Beneficiarios
CREATE TABLE [dimPadrones] (
  [idPadron]     INT    NOT NULL    IDENTITY ( 1 , 1 ),
  [Periodo]      INT    NOT NULL,
  [PersonaMonto] MONEY    NOT NULL,
     PRIMARY KEY ( [idPadron] ));

-- Creación de tabla de dimensión de Beneficiarios
CREATE TABLE [dimPersonas] (
  [IdPersona]            INT    NOT NULL    IDENTITY ( 1 , 1 ),
  [Persona]              NVARCHAR(40)    NOT NULL,
  [idEtario]             SMALLINT    NOT NULL,
  [Sexo]                 NCHAR(1)    NOT NULL,
  [idFamilia]            INT    NOT NULL,
  [Activo]        BIT    NOT NULL,
  [FactorActivo]         BIT    NOT NULL,
  [IdSituacion]          SMALLINT    NOT NULL,
  [VulnerabilidadActivo] BIT    NOT NULL,
     PRIMARY KEY ( [IdPersona] ));
CREATE NONCLUSTERED INDEX [IDIMPERSONAS1] ON [dimPersonas] (
      [idFamilia]);
CREATE NONCLUSTERED INDEX [IDIMPERSONAS2] ON [dimPersonas] (
      [idEtario]);
CREATE NONCLUSTERED INDEX [IDIMPERSONAS3] ON [dimPersonas] (
      [IdSituacion]);
ALTER TABLE [dimPersonas]
 ADD CONSTRAINT [IDIMPERSONAS2] FOREIGN KEY ( [idEtario] ) REFERENCES [dimEtarios]([idEtario]);
ALTER TABLE [dimPersonas]
 ADD CONSTRAINT [IDIMPERSONAS1] FOREIGN KEY ( [idFamilia] ) REFERENCES [dimFamilias]([idFamilia]);
ALTER TABLE [dimPersonas]
 ADD CONSTRAINT [IDIMPERSONAS3] FOREIGN KEY ( [IdSituacion] ) REFERENCES [dimSituaciones]([IdSituacion]);

-- Creación de tabla de dimensión de Programas
CREATE TABLE [dimProgramas] (
  [idPrograma]    SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [Programa]      NVARCHAR(40)    NOT NULL,
  [PersonaActivo] BIT    NOT NULL,
     PRIMARY KEY ( [idPrograma] ));

-- Creación de tabla de dimensión de Satisfacciones
CREATE TABLE [dimSatisfacciones] (
  [IdSatisfaccion]      SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [Periodo] INT    NOT NULL,
  [Nivel]               SMALLINT    NOT NULL,
  [idPrograma]          SMALLINT    NOT NULL,
     PRIMARY KEY ( [IdSatisfaccion] ));
CREATE NONCLUSTERED INDEX [IDIMSATISFACCIONES1] ON [dimSatisfacciones] ([idPrograma]);
ALTER TABLE [dimSatisfacciones]
 ADD CONSTRAINT [IDIMSATISFACCIONES1] FOREIGN KEY ( [idPrograma] ) REFERENCES [dimProgramas]([idPrograma]);

-- Creación de tabla de dimensión de Situaciones Sociales
CREATE TABLE [dimSituaciones] (
  [IdSituacion] SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [Situacion]   NVARCHAR(40)    NOT NULL,
     PRIMARY KEY ( [IdSituacion] ));

-- Creación de tabla de dimensión de Tarjetas Magnéticas
CREATE TABLE [dimTarjetas] (
  [IdTarjeta]     INT    NOT NULL    IDENTITY ( 1 , 1 ),
  [IdPersona]     INT    NOT NULL,
  [ActivoTarjeta] BIT    NOT NULL,
     PRIMARY KEY ( [IdTarjeta] ));
CREATE NONCLUSTERED INDEX [IDIMTARJETAS1] ON [dimTarjetas] (
      [IdPersona]);
ALTER TABLE [dimTarjetas]
 ADD CONSTRAINT [IDIMTARJETAS1] FOREIGN KEY ( [IdPersona] ) REFERENCES [dimPersonas]([IdPersona]);

-- Creación de tabla de dimensión de Transacciones
CREATE TABLE [dimTransacciones] (
  [IdTransaccion]    INT    NOT NULL    IDENTITY ( 1 , 1 ),
  [Fecha] DATETIME    NOT NULL,
  [Monto] MONEY    NOT NULL,
  [IdTarjeta]        INT    NOT NULL,
     PRIMARY KEY ( [IdTransaccion] ));
CREATE NONCLUSTERED INDEX [IDIMTRANSACCIONES1] ON [dimTransacciones] ([IdTarjeta]);
ALTER TABLE [dimTransacciones]
 ADD CONSTRAINT [IDIMTRANSACCIONES1] FOREIGN KEY ( [IdTarjeta] ) REFERENCES [dimTarjetas]([IdTarjeta]);

-- Creación de tabla de dimensión de Vulnerabilidades Sociales
CREATE TABLE [dimVulnerables] (
  [IdVulnerable] SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [Vulnerable]   NVARCHAR(40)    NOT NULL,
     PRIMARY KEY ( [IdVulnerable] ));

-- Tablas de Hechos

-- Creación de tabla de hechos Administración de Beneficiarios
CREATE TABLE [admPersonas] (
  [IdPersona]       INT    NOT NULL,
  [idCriterio]      SMALLINT    NOT NULL,
  [idPrograma]      SMALLINT    NOT NULL,
  [CantTot]         DECIMAL(11)    NOT NULL,
  [CantXEtario]     DECIMAL(11)    NOT NULL,
  [CantXLocalidad]  DECIMAL(11)    NOT NULL,
  [CantXGenero]     DECIMAL(11)    NOT NULL,
  [PorcCumCriterio] SMALLMONEY    NOT NULL,
     PRIMARY KEY ( [IdPersona],[idCriterio],[idPrograma] ));
CREATE NONCLUSTERED INDEX [IADMPERSONAS1] ON [admPersonas] (
      [idPrograma]);
CREATE NONCLUSTERED INDEX [IADMPERSONAS2] ON [admPersonas] (
      [idCriterio]);
ALTER TABLE [admPersonas]
 ADD CONSTRAINT [IADMPERSONAS3] FOREIGN KEY ( [IdPersona] ) REFERENCES [dimPersonas]([IdPersona]);
ALTER TABLE [admPersonas]
 ADD CONSTRAINT [IADMPERSONAS2] FOREIGN KEY ( [idCriterio] ) REFERENCES [dimCriterios]([idCriterio]);
ALTER TABLE [admPersonas]
 ADD CONSTRAINT [IADMPERSONAS1] FOREIGN KEY ( [idPrograma] ) REFERENCES [dimProgramas]([idPrograma]);

-- Creación de tabla de hechos Eficiencia de los Programas
CREATE TABLE [efiProgramas] (
  [IdPersona]      INT    NOT NULL,
  [IdSatisfaccion] SMALLINT    NOT NULL,
  [IdFecha]        SMALLINT    NOT NULL,
  [CostoOpera]     MONEY    NOT NULL,
  [CantMasAlta]    DECIMAL(11)    NOT NULL,
  [PromNivelSat]   MONEY    NOT NULL,
     PRIMARY KEY ( [IdPersona],[IdSatisfaccion],[IdFecha] ));
CREATE NONCLUSTERED INDEX [IEFIPROGRAMAS1] ON [efiProgramas] (
      [IdFecha]);
CREATE NONCLUSTERED INDEX [IEFIPROGRAMAS2] ON [efiProgramas] (
      [IdSatisfaccion]);
ALTER TABLE [efiProgramas]
 ADD CONSTRAINT [IEFIPROGRAMAS3] FOREIGN KEY ( [IdPersona] ) REFERENCES [dimPersonas]([IdPersona]);
ALTER TABLE [efiProgramas]
 ADD CONSTRAINT [IEFIPROGRAMAS2] FOREIGN KEY ( [IdSatisfaccion] ) REFERENCES [dimSatisfacciones]([IdSatisfaccion]);
ALTER TABLE [efiProgramas]
 ADD CONSTRAINT [IEFIPROGRAMAS1] FOREIGN KEY ( [IdFecha] ) REFERENCES [dimFechas]([IdFecha]);

-- Creación de tabla de hechos Participación Municipal
CREATE TABLE [participaMunicipal] (
  [IdNovedad]    SMALLINT    NOT NULL,
  [idPrograma]   SMALLINT    NOT NULL,
  [IdFecha]      SMALLINT    NOT NULL,
  [PromAltasMes] MONEY    NOT NULL,
  [CantBajasMes] DECIMAL(11)    NOT NULL,
  [PorcCrecim]   SMALLMONEY    NOT NULL,
     PRIMARY KEY ( [IdNovedad],[idPrograma],[IdFecha] ));
CREATE NONCLUSTERED INDEX [IPARTICIPAMUNICIPAL1] ON [participaMunicipal] ([IdFecha]);
CREATE NONCLUSTERED INDEX [IPARTICIPAMUNICIPAL2] ON [participaMunicipal] ([idPrograma]);
ALTER TABLE [participaMunicipal]
 ADD CONSTRAINT [IPARTICIPAMUNICIPAL3] FOREIGN KEY ( [IdNovedad] ) REFERENCES [dimNovedades]([IdNovedad]);
ALTER TABLE [participaMunicipal]
 ADD CONSTRAINT [IPARTICIPAMUNICIPAL2] FOREIGN KEY ( [idPrograma] ) REFERENCES [dimProgramas]([idPrograma]);
ALTER TABLE [participaMunicipal]
 ADD CONSTRAINT [IPARTICIPAMUNICIPAL1] FOREIGN KEY ( [IdFecha] ) REFERENCES [dimFechas]([IdFecha]);

-- Creación de tabla de hechos Uso de Tarjetas
CREATE TABLE [usoTarjetas] (
  [idPadron]       INT    NOT NULL,
  [IdTransaccion]  INT    NOT NULL,
  [IdFecha]        SMALLINT    NOT NULL,
  [TotMontoAsigna] MONEY    NOT NULL,
  [TotMontoGasto]  MONEY    NOT NULL,
  [CantTransacc]   DECIMAL(11)    NOT NULL,
     PRIMARY KEY ( [idPadron],[IdTransaccion],[IdFecha] ));
CREATE NONCLUSTERED INDEX [IUSOTARJETAS1] ON [usoTarjetas] (
      [IdFecha]);
CREATE NONCLUSTERED INDEX [IUSOTARJETAS2] ON [usoTarjetas] (
      [IdTransaccion]);
ALTER TABLE [usoTarjetas]
 ADD CONSTRAINT [IUSOTARJETAS3] FOREIGN KEY ( [idPadron] ) REFERENCES [dimPadrones]([idPadron]);
ALTER TABLE [usoTarjetas]
 ADD CONSTRAINT [IUSOTARJETAS2] FOREIGN KEY ( [IdTransaccion] ) REFERENCES [dimTransacciones]([IdTransaccion]);
ALTER TABLE [usoTarjetas]
 ADD CONSTRAINT [IUSOTARJETAS1] FOREIGN KEY ( [IdFecha] ) REFERENCES [dimFechas]([IdFecha]);

-- Creación de tabla de hechos Vulnerabilidad Social
CREATE TABLE [vulneraSocial] (
  [IdPersona]    INT    NOT NULL,
  [IdFactor]     SMALLINT    NOT NULL,
  [idPrograma]   SMALLINT    NOT NULL,
  [IdFecha]      SMALLINT    NOT NULL,
  [IdVulnerable] SMALLINT    NOT NULL,
  [PorcMejaro]   SMALLMONEY    NOT NULL,
  [PromPerma]    MONEY    NOT NULL,
  [CantFactor]   DECIMAL(11)    NOT NULL,
     PRIMARY KEY ( [IdPersona],[IdFactor],[idPrograma],[IdFecha],[IdVulnerable] ));
CREATE NONCLUSTERED INDEX [IVULNERASOCIAL1] ON [vulneraSocial] (
      [IdVulnerable]);
CREATE NONCLUSTERED INDEX [IVULNERASOCIAL2] ON [vulneraSocial] (
      [IdFecha]);
CREATE NONCLUSTERED INDEX [IVULNERASOCIAL3] ON [vulneraSocial] (
      [idPrograma]);
CREATE NONCLUSTERED INDEX [IVULNERASOCIAL4] ON [vulneraSocial] (
      [IdFactor]);
ALTER TABLE [vulneraSocial]
 ADD CONSTRAINT [IVULNERASOCIAL5] FOREIGN KEY ( [IdPersona] ) REFERENCES [dimPersonas]([IdPersona]);
ALTER TABLE [vulneraSocial]
 ADD CONSTRAINT [IVULNERASOCIAL4] FOREIGN KEY ( [IdFactor] ) REFERENCES [dimFactores]([IdFactor]);
ALTER TABLE [vulneraSocial]
 ADD CONSTRAINT [IVULNERASOCIAL3] FOREIGN KEY ( [idPrograma] ) REFERENCES [dimProgramas]([idPrograma]);
ALTER TABLE [vulneraSocial]
 ADD CONSTRAINT [IVULNERASOCIAL2] FOREIGN KEY ( [IdFecha] ) REFERENCES [dimFechas]([IdFecha]);
ALTER TABLE [vulneraSocial]
 ADD CONSTRAINT [IVULNERASOCIAL1] FOREIGN KEY ( [IdVulnerable] ) REFERENCES [dimVulnerables]([IdVulnerable]);
