-- Base de Datos

-- Creación de base de datos Secretaria
CREATE DATABASE [Secretaria];

-- Selección de base de datos Secretaria
USE [Secretaria];

-- Tablas

-- Creación de tabla de Bancos
CREATE TABLE [Banco] (
  [BancoId]        SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [BancoNombre]    NVARCHAR(40)    NOT NULL,
  [BancoDomicilio] NVARCHAR(1024)    NOT NULL,
  [BancoContacto]  NVARCHAR(40)    NOT NULL,
  [BancoTelefono]  NCHAR(20)    NOT NULL,
  [BancoEmail]     NVARCHAR(100)    NOT NULL,
  [BancoWeb]       NVARCHAR(1000)    NOT NULL,
     PRIMARY KEY ( [BancoId] ));

-- Creación de tabla de Barrios
CREATE TABLE [Barrio] (
  [BarrioId]     SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [BarrioNombre] NVARCHAR(40)    NOT NULL,
  [LocalidadId]  SMALLINT    NOT NULL,
  [BarrioCodigo]  SMALLINT    NULL,
     PRIMARY KEY ( [BarrioId] ));
CREATE NONCLUSTERED INDEX [IBARRIO1] ON [Barrio] (
      [LocalidadId]);
ALTER TABLE [Barrio]
 ADD CONSTRAINT [IBARRIO1] FOREIGN KEY ( [LocalidadId] ) REFERENCES [Localidad]([LocalidadId]);

-- Creación de tabla de Comprobantes
CREATE TABLE [Comprobante] (
  [ComprobanteId]    INT    NOT NULL    IDENTITY ( 1 , 1 ),
  [ComprobanteTipo]  NCHAR(3)    NOT NULL,
  [ComprobanteNum]   INT    NOT NULL,
  [ComprobanteLetra] NCHAR(1)    NOT NULL,
  [ComprobanteFecha] DATETIME    NOT NULL,
  [ComprobanteMonto] MONEY    NOT NULL,
     PRIMARY KEY ( [ComprobanteId] ));

-- Creación de tabla de Criterios de Inclusión
CREATE TABLE [Criterio] (
  [CriterioId]          SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [CriterioNombre]      NVARCHAR(40)    NOT NULL,
  [CriterioDescripcion] NVARCHAR(200)    NOT NULL,
     PRIMARY KEY ( [CriterioId] ));

-- Creación de tabla de Cuentas Bancarias
CREATE TABLE [Cuenta] (
  [CuentaId]    INT    NOT NULL    IDENTITY ( 1 , 1 ),
  [BancoId]     SMALLINT    NOT NULL,
  [CuentaNum]   INT    NOT NULL,
  [CuentaCBU]   DECIMAL(12)    NOT NULL,
  [CuentaAlias] NCHAR(20)    NOT NULL,
  [PersonaId]   INT    NOT NULL,
  [CuentaSaldo] MONEY    NOT NULL,
  [CuentaTipo]  NCHAR(2)    NOT NULL,
     PRIMARY KEY ( [CuentaId] ));
CREATE NONCLUSTERED INDEX [ICUENTA1] ON [Cuenta] (
      [PersonaId]);
CREATE NONCLUSTERED INDEX [ICUENTA2] ON [Cuenta] (
      [BancoId]);
ALTER TABLE [Cuenta]
 ADD CONSTRAINT [ICUENTA2] FOREIGN KEY ( [BancoId] ) REFERENCES [Banco]([BancoId]);
ALTER TABLE [Cuenta]
 ADD CONSTRAINT [ICUENTA1] FOREIGN KEY ( [PersonaId] ) REFERENCES [Persona]([PersonaId]);

-- Creación de tabla de Departamento
CREATE TABLE [Departamento] (
  [DepartamentoId]     SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [DepartamentoNombre] NVARCHAR(40)    NOT NULL,
     PRIMARY KEY ( [DepartamentoId] ));

-- Creación de tabla de Grupos Etarios
CREATE TABLE [Etario] (
  [EtarioId]      SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [EtarioNombre]  NVARCHAR(40)    NOT NULL,
  [EtarioEdadMin] SMALLINT    NOT NULL,
  [EtarioEdadMax] SMALLINT    NOT NULL,
     PRIMARY KEY ( [EtarioId] ));

-- Creación de tabla de Factores
CREATE TABLE [Factor] (
  [FactorId]          SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [FactorNombre]      NVARCHAR(40)    NOT NULL,
  [FactorDescripcion] NVARCHAR(200)    NOT NULL,
     PRIMARY KEY ( [FactorId] ));

-- Creación de tabla de Familias
CREATE TABLE [Familia] (
  [FamiliaId]          INT    NOT NULL    IDENTITY ( 1 , 1 ),
  [FamiliaDomicilio]   NVARCHAR(1024)    NOT NULL,
  [FamiliaBarrioId]    SMALLINT    NOT NULL,
  [FamiliaLocalidadId] SMALLINT    NOT NULL,
  [MunicipioId]        SMALLINT    NOT NULL,
  [FamiliaCodigo]        NVARCHAR(10)    NOT NULL,
     PRIMARY KEY ( [FamiliaId] ));
CREATE NONCLUSTERED INDEX [IFAMILIA1] ON [Familia] (
      [MunicipioId]);
CREATE NONCLUSTERED INDEX [IFAMILIA2] ON [Familia] (
      [FamiliaBarrioId]);
CREATE NONCLUSTERED INDEX [IFAMILIA3] ON [Familia] (
      [FamiliaLocalidadId]);
ALTER TABLE [Familia]
 ADD CONSTRAINT [IFAMILIA1] FOREIGN KEY ( [MunicipioId] ) REFERENCES [Municipio]([MunicipioId]);
ALTER TABLE [Familia]
 ADD CONSTRAINT [IFAMILIA2] FOREIGN KEY ( [FamiliaBarrioId] ) REFERENCES [Barrio]([BarrioId]);
ALTER TABLE [Familia]
 ADD CONSTRAINT [IFAMILIA3] FOREIGN KEY ( [FamiliaLocalidadId] ) REFERENCES [Localidad]([LocalidadId]);

-- Creación de tabla de Localidades
CREATE TABLE [Localidad] (
  [LocalidadId]     SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [LocalidadNombre] NVARCHAR(40)    NOT NULL,
  [LocalidadCodPos] NCHAR(6)    NOT NULL,
  [DepartamentoId]  SMALLINT    NOT NULL,
  [MunicioioId]  SMALLINT    NOT NULL,
     PRIMARY KEY ( [LocalidadId] ));
CREATE NONCLUSTERED INDEX [ILOCALIDAD1] ON [Localidad] (
      [DepartamentoId]);
ALTER TABLE [Localidad]
 ADD CONSTRAINT [ILOCALIDAD1] FOREIGN KEY ( [DepartamentoId] ) REFERENCES [Departamento]([DepartamentoId]);
ALTER TABLE [Localidad]
 ADD CONSTRAINT [ILOCALIDAD2] FOREIGN KEY ( [MunicipioId] ) REFERENCES [Municipio]([MunicipioId]);

-- Creación de tabla de Municipios
CREATE TABLE [Municipio] (
  [MunicipioId]         SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [MunicipioNombre]     NVARCHAR(40)    NOT NULL,
  [DepartamentoId]      SMALLINT    NOT NULL,
  [MunicipioDomicilio]  NVARCHAR(1024)    NOT NULL,
  [MunicipioTelefono]   NCHAR(20)    NOT NULL,
  [MunicipioEmail]      NVARCHAR(100)    NOT NULL,
  [MunicipioWeb]        NVARCHAR(1000)    NOT NULL,
  [MunicipioSuperficie] SMALLMONEY    NOT NULL,
  [MunicipioPoblacion]  INT    NOT NULL,
  [MunicipioIntendente] NVARCHAR(40)    NOT NULL,
  [MunicipioContacto]   NVARCHAR(40)    NOT NULL,
  [MunicipioCodigo]   NVARCHAR(10)    NOT NULL,
     PRIMARY KEY ( [MunicipioId] ));
CREATE NONCLUSTERED INDEX [IMUNICIPIO1] ON [Municipio] (
      [DepartamentoId]);
ALTER TABLE [Municipio]
 ADD CONSTRAINT [IMUNICIPIO1] FOREIGN KEY ( [DepartamentoId] ) REFERENCES [Departamento] ([DepartamentoId]);

-- Creación de tabla de Novedades
CREATE TABLE [Novedad] (
  [NovedadId]      INT    NOT NULL    IDENTITY ( 1 , 1 ),
  [NovedadPeriodo] INT    NOT NULL,
  [ProgramaId]     SMALLINT    NOT NULL,
  [NovedadActivo]  BIT    NOT NULL,
  [MunicipioId]    SMALLINT    NOT NULL,
     PRIMARY KEY ( [NovedadId] ));
CREATE NONCLUSTERED INDEX [INOVEDAD2] ON [Novedad] (
      [ProgramaId]);
CREATE NONCLUSTERED INDEX [INOVEDAD1] ON [Novedad] (
      [MunicipioId]);
ALTER TABLE [Novedad]
 ADD CONSTRAINT [INOVEDAD2] FOREIGN KEY ( [ProgramaId] ) REFERENCES [Programa]([ProgramaId]);
ALTER TABLE [Novedad]
 ADD CONSTRAINT [INOVEDAD1] FOREIGN KEY ( [MunicipioId] ) REFERENCES [Municipio]([MunicipioId]);

-- Creación de tabla de Novedades de Personas
CREATE TABLE [NovedadPersona] (
  [NovedadId]           INT    NOT NULL,
  [PersonaId]           INT    NOT NULL,
  [NovedadPersonaFecha] DATETIME    NOT NULL,
  [NovedadPersonaTipo]  NCHAR(3)    NOT NULL,
     PRIMARY KEY ( [NovedadId],[PersonaId] ));
CREATE NONCLUSTERED INDEX [INOVEDADPERSONA1] ON [NovedadPersona] ([PersonaId]);
ALTER TABLE [NovedadPersona]
 ADD CONSTRAINT [INOVEDADPERSONA2] FOREIGN KEY ( [NovedadId] ) REFERENCES [Novedad] ([NovedadId]);
ALTER TABLE [NovedadPersona]
 ADD CONSTRAINT [INOVEDADPERSONA1] FOREIGN KEY ( [PersonaId] ) REFERENCES [Persona] ([PersonaId]);

-- Creación de tabla de Gatos Operativos
CREATE TABLE [Operativo] (
  [ProgramaId]      SMALLINT    NOT NULL,
  [OperativoId]     INT    NOT NULL,
  [OperativoFecha]  DATETIME    NOT NULL,
  [OperativoMonto]  MONEY    NOT NULL,
  [OperativoActivo] BIT    NOT NULL,
  [ComprobanteId]   INT    NOT NULL,
     PRIMARY KEY ( [ProgramaId],[OperativoId] ));
CREATE NONCLUSTERED INDEX [IOPERATIVO2] ON [Operativo] (
      [ComprobanteId]);
ALTER TABLE [Operativo]
 ADD CONSTRAINT [IOPERATIVO1] FOREIGN KEY ( [ProgramaId] ) REFERENCES [Programa]([ProgramaId]);
ALTER TABLE [Operativo]
 ADD CONSTRAINT [IOPERATIVO2] FOREIGN KEY ( [ComprobanteId] ) REFERENCES [Comprobante]([ComprobanteId]);

-- Creación de tabla de Padrones
CREATE TABLE [Padron] (
  [PadronId]      INT    NOT NULL    IDENTITY ( 1 , 1 ),
  [PadronPeriodo] INT    NOT NULL,
  [PadronFecha]   DATETIME    NOT NULL,
  [ProgramaId]    SMALLINT    NOT NULL,
     PRIMARY KEY ( [PadronId] ));
CREATE NONCLUSTERED INDEX [IPADRON1] ON [Padron] (
      [ProgramaId]);
ALTER TABLE [Padron]
 ADD CONSTRAINT [IPADRON1] FOREIGN KEY ( [ProgramaId] ) REFERENCES [Programa]([ProgramaId]);

-- Creación de tabla de Padrones de Personas
CREATE TABLE [PadronPersona] (
  [PadronId]           INT    NOT NULL,
  [PersonaId]          INT    NOT NULL,
  [PadronPersonaMonto] MONEY    NOT NULL,
     PRIMARY KEY ( [PadronId],[PersonaId] ));
CREATE NONCLUSTERED INDEX [IPADRONPERSONA1] ON [PadronPersona] (
      [PersonaId]);
ALTER TABLE [PadronPersona]
 ADD CONSTRAINT [IPADRONPERSONA2] FOREIGN KEY ( [PadronId] ) REFERENCES [Padron]([PadronId]);
ALTER TABLE [PadronPersona]
 ADD CONSTRAINT [IPADRONPERSONA1] FOREIGN KEY ( [PersonaId] ) REFERENCES [Persona]([PersonaId]);

-- Creación de tabla de Parentescos
CREATE TABLE [Parentesco] (
  [ParentescoId]     SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [ParentescoNombre] NVARCHAR(40)    NOT NULL,
     PRIMARY KEY ( [ParentescoId] ));

-- Creación de tabla de Personas
CREATE TABLE [Persona] (
  [PersonaId]          INT    NOT NULL    IDENTITY ( 1 , 1 ),
  [PersonaNombre]      NVARCHAR(40)    NOT NULL,
  [FamiliaId]          INT    NOT NULL,
  [PersonaFecNac]      DATETIME    NOT NULL,
  [EtarioId]           SMALLINT    NOT NULL,
  [PersonaSexo]        NCHAR(1)    NOT NULL,
  [PersonaFechaAlta]   DATETIME    NOT NULL,
  [PersonaFechaBaja]   DATETIME    NOT NULL,
  [PersonaObservacion] NVARCHAR(200)    NOT NULL,
  [SituacionId]        SMALLINT    NOT NULL,
  [ParentescoId]       SMALLINT    NOT NULL,
  [PersonaEmail]       NVARCHAR(100)    NOT NULL,
  [PersonaTelefono]    NCHAR(20)    NOT NULL,
  [PersonaActivo]      BIT    NOT NULL,
  [PersonaCodigo]    NCHAR(10)    NOT NULL,
  [PersonaTipDoc]    NCHAR(3)    NOT NULL,
  [PersonaNroDoc]    INT    NOT NULL,
     PRIMARY KEY ( [PersonaId] ));
CREATE NONCLUSTERED INDEX [IPERSONA1] ON [Persona] (
      [EtarioId]);
CREATE NONCLUSTERED INDEX [IPERSONA2] ON [Persona] (
      [FamiliaId]);
CREATE NONCLUSTERED INDEX [IPERSONA3] ON [Persona] (
      [ParentescoId]);
CREATE NONCLUSTERED INDEX [IPERSONA4] ON [Persona] (
      [SituacionId]);
ALTER TABLE [Persona]
 ADD CONSTRAINT [IPERSONA2] FOREIGN KEY ( [FamiliaId] ) REFERENCES [Familia]([FamiliaId]);
ALTER TABLE [Persona]
 ADD CONSTRAINT [IPERSONA1] FOREIGN KEY ( [EtarioId] ) REFERENCES [Etario]([EtarioId]);
ALTER TABLE [Persona]
 ADD CONSTRAINT [IPERSONA4] FOREIGN KEY ( [SituacionId] ) REFERENCES [Situacion]([SituacionId]);
ALTER TABLE [Persona]
 ADD CONSTRAINT [IPERSONA3] FOREIGN KEY ( [ParentescoId] ) REFERENCES [Parentesco]([ParentescoId]);

-- Creación de tabla de Personas por Criterio
CREATE TABLE [PersonaCriterio] (
  [PersonaId]                 INT    NOT NULL,
  [CriterioId]                 SMALLINT    NOT NULL,
  [PersonaCriterioFechaAlta]   DATETIME    NOT NULL,
  [PersonaCriterioFechaBaja]   DATETIME    NOT NULL,
  [PersonaCriterioObservacion] NVARCHAR(200)    NOT NULL,
  [PersonaCriterioActivo]      BIT    NOT NULL,
     PRIMARY KEY ( [PersonaId],[CriterioId] ));
CREATE NONCLUSTERED INDEX [IPERSONACRITERIO1] ON [PersonaCriterio] ([CriterioId]);
ALTER TABLE [PersonaCriterio]
 ADD CONSTRAINT [IPERSONACRITERIO2] FOREIGN KEY ( [PersonaId] ) REFERENCES [Persona]([PersonaId]);
ALTER TABLE [PersonaCriterio]
 ADD CONSTRAINT [IPERSONACRITERIO1] FOREIGN KEY ( [CriterioId] ) REFERENCES [Criterio]([CriterioId]);

-- Creación de tabla de Personas por Factor
CREATE TABLE [PersonaFactor] (
  [PersonaId]                INT    NOT NULL,
  [FactorId]                 SMALLINT    NOT NULL,
  [PersonaFactorFechaAlta]   DATETIME    NOT NULL,
  [PersonaFactorFechaBaja]   DATETIME    NOT NULL,
  [PersonaFactorActivo]      BIT    NOT NULL,
  [PersonaFactorObservacion] NVARCHAR(200)    NOT NULL,
     PRIMARY KEY ( [PersonaId],[FactorId] ));
CREATE NONCLUSTERED INDEX [IPERSONAFACTOR1] ON [PersonaFactor] (
      [FactorId]);
ALTER TABLE [PersonaFactor]
 ADD CONSTRAINT [IPERSONAFACTOR2] FOREIGN KEY ( [PersonaId] ) REFERENCES [Persona]([PersonaId]);
ALTER TABLE [PersonaFactor]
 ADD CONSTRAINT [IPERSONAFACTOR1] FOREIGN KEY ( [FactorId] ) REFERENCES [Factor]([FactorId]);

-- Creación de tabla de Personas por Prestación
CREATE TABLE [PersonaPrestacion] (
  [PersonaId]                    INT    NOT NULL,
  [PrestacionId]                 SMALLINT    NOT NULL,
  [PersonaPrestacionActivo]      BIT    NOT NULL,
  [PersonaPrestacionObservacion] NVARCHAR(200)    NOT NULL,
  [PersonaPrestacionFechaAlta]   DATETIME    NOT NULL,
  [PersonaPrestacionFechaBaja]   DATETIME    NOT NULL,
     PRIMARY KEY ( [PersonaId],[PrestacionId] ));
CREATE NONCLUSTERED INDEX [IPERSONAPRESTACION1] ON [PersonaPrestacion] ([PrestacionId]);
ALTER TABLE [PersonaPrestacion]
 ADD CONSTRAINT [IPERSONAPRESTACION2] FOREIGN KEY ( [PersonaId] ) REFERENCES [Persona]([PersonaId]);
ALTER TABLE [PersonaPrestacion]
 ADD CONSTRAINT [IPERSONAPRESTACION1] FOREIGN KEY ( [PrestacionId] ) REFERENCES [Prestacion]([PrestacionId]);

-- Creación de tabla de Personas por Vulnerabilidades
CREATE TABLE [PersonaVulnerabilidad] (
  [PersonaId]                      INT    NOT NULL,
  [VulnerabilidadId]               SMALLINT    NOT NULL,
  [PersonaVulnerabilidadFechaAlta] DATETIME    NOT NULL,
  [PersonaVulnerabilidadFechaBaja] DATETIME    NOT NULL,
  [PersonaVulnerabilidadActivo]    BIT    NOT NULL,
  [PersonaVulnerabilidadObservaci] NVARCHAR(200)    NOT NULL,
     PRIMARY KEY ( [PersonaId],[VulnerabilidadId] ));
CREATE NONCLUSTERED INDEX [IPERSONAVULNERABILIDAD1] ON [PersonaVulnerabilidad] ([VulnerabilidadId]);
ALTER TABLE [PersonaVulnerabilidad]
 ADD CONSTRAINT [IPERSONAVULNERABILIDAD2] FOREIGN KEY ( [PersonaId] ) REFERENCES [Persona]([PersonaId]);
ALTER TABLE [PersonaVulnerabilidad]
 ADD CONSTRAINT [IPERSONAVULNERABILIDAD1] FOREIGN KEY ( [VulnerabilidadId] ) REFERENCES [Vulnerabilidad]([VulnerabilidadId]);

-- Creación de tabla de Prestaciones
CREATE TABLE [Prestacion] (
  [PrestacionId]          SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [PrestacionNombre]      NVARCHAR(40)    NOT NULL,
  [PrestacionMonto]       MONEY    NOT NULL,
  [PrestacionBancarizada] BIT    NOT NULL,
  [PrestacionEdadMin]     SMALLINT    NOT NULL,
  [PresacionEdadMax]      SMALLINT    NOT NULL,
  [PrestacionEdadMinMes]  SMALLINT    NOT NULL,
     PRIMARY KEY ( [PrestacionId] ));

-- Creación de tabla de Prestaciones por Criterios
CREATE TABLE [PrestacionCriterio] (
  [PrestacionId]                  SMALLINT    NOT NULL,
  [CriterioId]                    SMALLINT    NOT NULL,
  [PrestacionCriterioFechaAlta]   DATETIME    NOT NULL,
  [PrestacionCriterioFechaBaja]   DATETIME    NOT NULL,
  [PrestacionCriterioActivo]      BIT    NOT NULL,
  [PrestacionCriterioObservacion] NVARCHAR(200)    NOT NULL,
     PRIMARY KEY ( [PrestacionId],[CriterioId] ));
CREATE NONCLUSTERED INDEX [IPRESTACIONCRITERIO1] ON [PrestacionCriterio] ([CriterioId]);
ALTER TABLE [PrestacionCriterio]
 ADD CONSTRAINT [IPRESTACIONCRITERIO2] FOREIGN KEY ( [PrestacionId] ) REFERENCES [Prestacion]([PrestacionId]);
ALTER TABLE [PrestacionCriterio]
 ADD CONSTRAINT [IPRESTACIONCRITERIO1] FOREIGN KEY ( [CriterioId] ) REFERENCES [Criterio]([CriterioId]);

-- Creación de tabla de Programas 
CREATE TABLE [Programa] (
  [ProgramaId]     SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [ProgramaNombre] NVARCHAR(40)    NOT NULL,
     PRIMARY KEY ( [ProgramaId] ));

-- Creación de tabla de Programas por Personas
CREATE TABLE [ProgramaPersona] (
  [ProgramaId]                 SMALLINT    NOT NULL,
  [PersonaId]                  INT    NOT NULL,
  [ProgramaPersonaFechaAlta]   DATETIME    NOT NULL,
  [ProgramaPersonaFechaBaja]   DATETIME    NOT NULL,
  [ProgramaPersonaActivo]      BIT    NOT NULL,
  [ProgramaPersonaObservacion] NVARCHAR(200)    NOT NULL,
     PRIMARY KEY ( [ProgramaId],[PersonaId] ));
CREATE NONCLUSTERED INDEX [IPROGRAMAPERSONA1] ON [ProgramaPersona] ([PersonaId]);
ALTER TABLE [ProgramaPersona]
 ADD CONSTRAINT [IPROGRAMAPERSONA2] FOREIGN KEY ( [ProgramaId] ) REFERENCES [Programa]([ProgramaId]);
ALTER TABLE [ProgramaPersona]
 ADD CONSTRAINT [IPROGRAMAPERSONA1] FOREIGN KEY ( [PersonaId] ) REFERENCES [Persona]([PersonaId]);

-- Creación de tabla de Satisfacciones
CREATE TABLE [Satisfaccion] (
  [SatisfaccionId]      SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [SatisfaccionPeriodo] INT    NOT NULL,
  [ProgramaId]          SMALLINT    NOT NULL,
     PRIMARY KEY ( [SatisfaccionId] ));
CREATE NONCLUSTERED INDEX [ISATISFACCION1] ON [Satisfaccion] (
      [ProgramaId]);
ALTER TABLE [Satisfaccion]
 ADD CONSTRAINT [ISATISFACCION1] FOREIGN KEY ( [ProgramaId] ) REFERENCES [Programa]([ProgramaId]);

-- Creación de tabla de Satisfacciones por Personas 
CREATE TABLE [SatisfaccionPersona] (
  [SatisfaccionId]           SMALLINT    NOT NULL,
  [PersonaId]                SMALLINT    NOT NULL,
  [SatisfaccionPersonaNivel] SMALLINT    NOT NULL,
     PRIMARY KEY ( [SatisfaccionId],[PersonaId] ));
CREATE NONCLUSTERED INDEX [ISATISFACCIONPERSONA1] ON [SatisfaccionPersona] ([PersonaId]);
ALTER TABLE [SatisfaccionPersona]
 ADD CONSTRAINT [ISATISFACCIONPERSONA2] FOREIGN KEY ( [SatisfaccionId] ) REFERENCES [Satisfaccion]([SatisfaccionId]);
ALTER TABLE [SatisfaccionPersona]
 ADD CONSTRAINT [ISATISFACCIONPERSONA1] FOREIGN KEY ( [PersonaId] ) REFERENCES [Persona]([PersonaId]);

-- Creación de tabla de Situaciones
CREATE TABLE [Situacion] (
  [SituacionId]          SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [SituacionNombre]      NVARCHAR(40)    NOT NULL,
  [SituacionDescripcion] NVARCHAR(200)    NOT NULL,
     PRIMARY KEY ( [SituacionId] ));

-- Creación de tabla de Tarjetas Magnéticas
CREATE TABLE [Tarjeta] (
  [TarjetaId]          INT    NOT NULL    IDENTITY ( 1 , 1 ),
  [TarjetaNum]         DECIMAL(16)    NOT NULL,
  [TarjetaActivo]      BIT    NOT NULL,
  [BancoId]            SMALLINT    NOT NULL,
  [TarjetaFechaAlta]   DATETIME    NOT NULL,
  [TarjetaFechaBaja]   DATETIME    NOT NULL,
  [TarjetaObservacion] NVARCHAR(200)    NOT NULL,
  [TarjetaInicio]      SMALLINT    NOT NULL,
  [TarjetaFin]         SMALLINT    NOT NULL,
  [PersonaId]          SMALLINT    NOT NULL,
     PRIMARY KEY ( [TarjetaId] ));
CREATE NONCLUSTERED INDEX [ITARJETA1] ON [Tarjeta] (
      [BancoId]);
CREATE NONCLUSTERED INDEX [ITARJETA2] ON [Tarjeta] (
      [PersonaId]);
ALTER TABLE [Tarjeta]
 ADD CONSTRAINT [ITARJETA1] FOREIGN KEY ( [BancoId] ) REFERENCES [Banco]([BancoId]);
ALTER TABLE [Tarjeta]
 ADD CONSTRAINT [ITARJETA2] FOREIGN KEY ( [PersonaId] ) REFERENCES [Persona]([PersonaId]);

-- Creación de tabla de Tiempo
CREATE TABLE [Tiempo] (
  [TiempoId]                 INT    NOT NULL    IDENTITY ( 1 , 1 ),
  [NovedadPeriodo]           INT    NOT NULL,
  [OperativoFecha]           DATETIME    NOT NULL,
  [PadronPeriodo]            INT    NOT NULL,
  [ProgramaPersonaFechaAlta] DATETIME    NOT NULL,
  [SatisfaccionPeriodo]      INT    NOT NULL,
  [TransaccionFecha]         DATETIME    NOT NULL,
     PRIMARY KEY ( [TiempoId] ));

-- Creación de tabla de Transacciones
CREATE TABLE [Transaccion] (
  [TransaccionCodigo] NCHAR(10)    NOT NULL,
  [TransaccionFecha]  DATETIME    NOT NULL,
  [TransaccionMonto]  MONEY    NOT NULL,
  [TarjetaId]         INT    NOT NULL,
     PRIMARY KEY ( [TransaccionCodigo] ));
CREATE NONCLUSTERED INDEX [ITRANSACCION1] ON [Transaccion] (
      [TarjetaId]);
ALTER TABLE [Transaccion]
 ADD CONSTRAINT [ITRANSACCION1] FOREIGN KEY ( [TarjetaId] ) REFERENCES [Tarjeta]([TarjetaId]);

-- Creación de tabla de Vulnerabilidades
CREATE TABLE [Vulnerabilidad] (
  [VulnerabilidadId]          SMALLINT    NOT NULL    IDENTITY ( 1 , 1 ),
  [VulnerabilidadNombre]      NVARCHAR(40)    NOT NULL,
  [VulnerabilidadDescripcion] NVARCHAR(200)    NOT NULL,
     PRIMARY KEY ( [VulnerabilidadId] ));

-- Funciones

-- Función devolver la Fecha actual
CREATE FUNCTION fn_FechaHoy()
RETURNS DATE
AS
BEGIN
    RETURN CAST(GETDATE() AS DATE);
END;
GO

-- Función devolver la Cantidad de Vulnerabilidades por Persona
CREATE FUNCTION fn_CantVulPerso
(
    @PersonaId INT
)
RETURNS INT
AS
BEGIN
    DECLARE @Cantidad INT;
    SELECT @Cantidad = COUNT(*)
    FROM [PersonaVulnerabilidad]
    WHERE [PersonaId] = @PersonaId
      AND [PersonaVulnerabilidadActivo] = 1;
    RETURN ISNULL(@Cantidad, 0);
END;
GO

-- Función devolver la Cantidad de Vulnerabilidades Superadas por Persona
CREATE FUNCTION fn_CantVulPersoSup
(
    @PersonaId INT
)
RETURNS INT
AS
BEGIN
    DECLARE @Cantidad INT;
    SELECT @Cantidad = COUNT(*)
    FROM [PersonaVulnerabilidad]
    WHERE [PersonaId] = @PersonaId
      AND [PersonaVulnerabilidadActivo] = 1;
    RETURN ISNULL(@Cantidad, 0);
END;
GO

-- Función devolver la Cantidad de Días de Permanencia de una Persona en un Programa
CREATE FUNCTION fn_CantDiaPerm
(
    @PersonaId INT,
    @ProgramaId SMALLINT
)
RETURNS INT
AS
BEGIN
    DECLARE @Dias INT;
    DECLARE @FechaAlta DATETIME;
    DECLARE @FechaBaja DATETIME;
    DECLARE @Activo BIT;
    SELECT 
        @FechaAlta = [ProgramaPersonaFechaAlta],
        @FechaBaja = [ProgramaPersonaFechaBaja],
        @Activo = [ProgramaPersonaActivo]
    FROM [ProgramaPersona]
    WHERE [PersonaId] = @PersonaId 
      AND [ProgramaId] = @ProgramaId;
    IF @FechaAlta IS NULL
        RETURN 0;
    IF @Activo = 1
        SET @Dias = DATEDIFF(DAY, @FechaAlta, GETDATE());
    ELSE
        SET @Dias = DATEDIFF(DAY, @FechaAlta, @FechaBaja);
    RETURN @Dias;
END;
GO

-- Función devolver Cantidad de Satisfacción de Personas de un Programa por Período
CREATE FUNCTION fn_CantSatPersoProg
(
    @ProgramaId SMALLINT,
    @Periodo INT
)
RETURNS INT
AS
BEGIN
    DECLARE @Cantidad INT;
    SELECT @Cantidad = COUNT(SP.[PersonaId])
    FROM [Satisfaccion] S
    INNER JOIN [SatisfaccionPersona] SP ON S.[SatisfaccionId] = SP.[SatisfaccionId]
    WHERE S.[ProgramaId] = @ProgramaId
      AND S.[SatisfaccionPeriodo] = @Periodo;
    RETURN ISNULL(@Cantidad, 0);
END;
GO

-- Función devolver Sumatoria de Satisfacción de Personas de un Programa por Período
CREATE FUNCTION fn_SumMesSatPersoProg
(
    @ProgramaId SMALLINT,
    @Periodo INT
)
RETURNS BIGINT
AS
BEGIN
    DECLARE @Sumatoria BIGINT;

    SELECT @Sumatoria = SUM(CAST(SP.[SatisfaccionPersonaNivel] AS BIGINT))
    FROM [Satisfaccion] S
    INNER JOIN [SatisfaccionPersona] SP ON S.[SatisfaccionId] = SP.[SatisfaccionId]
    WHERE S.[ProgramaId] = @ProgramaId
      AND S.[SatisfaccionPeriodo] = @Periodo;
    RETURN ISNULL(@Sumatoria, 0);
END;
GO

-- Función devolver Cantidad de Altas Mensual por Municipio
CREATE FUNCTION fn_CantAltasMesMuni
(
    @MunicipioId SMALLINT,
    @Periodo INT
)
RETURNS INT
AS
BEGIN
    DECLARE @CantidadAltas INT;
    SELECT @CantidadAltas = COUNT(NP.[PersonaId])
    FROM [Novedad] N
    INNER JOIN [NovedadPersona] NP ON N.[NovedadId] = NP.[NovedadId]
    WHERE N.[MunicipioId] = @MunicipioId
      AND N.[NovedadPeriodo] = @Periodo
      AND NP.[NovedadPersonaTipo] = 'ALT';
    RETURN ISNULL(@CantidadAltas, 0);
END;
GO

-- Función devolver Cantidad de Bajas Mensual por Municipio
CREATE FUNCTION fn_CantBajasMesMuni
(
    @MunicipioId SMALLINT,
    @Periodo INT
)
RETURNS INT
AS
BEGIN
    DECLARE @CantidadAltas INT;
    SELECT @CantidadAltas = COUNT(NP.[PersonaId])
    FROM [Novedad] N
    INNER JOIN [NovedadPersona] NP ON N.[NovedadId] = NP.[NovedadId]
    WHERE N.[MunicipioId] = @MunicipioId
      AND N.[NovedadPeriodo] = @Periodo
      AND NP.[NovedadPersonaTipo] = 'BAJ';
    RETURN ISNULL(@CantidadAltas, 0);
END;
GO

-- Función devolver Cantidad de Altas por Municipio
CREATE FUNCTION fn_CantAltasMuni
(
    @MunicipioId SMALLINT
)
RETURNS INT
AS
BEGIN
    DECLARE @Cantidad INT;
    SELECT @Cantidad = COUNT(NP.[PersonaId])
    FROM [Novedad] N
    INNER JOIN [NovedadPersona] NP ON N.[NovedadId] = NP.[NovedadId]
    WHERE N.[MunicipioId] = @MunicipioId
      AND NP.[NovedadPersonaTipo] = 'ALT'
      AND N.[NovedadActivo] = 1; 
    RETURN ISNULL(@Cantidad, 0);
END;
GO

-- Función devolver Cantidad de Bajas por Municipio
CREATE FUNCTION dbo.fn_CantBajasMuni
(
    @MunicipioId SMALLINT
)
RETURNS INT
AS
BEGIN
    DECLARE @Cantidad INT;
    SELECT @Cantidad = COUNT(NP.[PersonaId])
    FROM [Novedad] N
    INNER JOIN [NovedadPersona] NP ON N.[NovedadId] = NP.[NovedadId]
    WHERE N.[MunicipioId] = @MunicipioId
      AND NP.[NovedadPersonaTipo] = 'BAJ' 
      AND N.[NovedadActivo] = 1;
    RETURN ISNULL(@Cantidad, 0);
END;
GO

-- Función devolver Cantidad de Personas por Municipio
CREATE FUNCTION fn_CantPersoMuni
(
    @MunicipioId SMALLINT
)
RETURNS INT
AS
BEGIN
    DECLARE @Cantidad INT;
    SELECT @Cantidad = COUNT(P.[PersonaId])
    FROM [Persona] P
    INNER JOIN [Familia] F ON P.[FamiliaId] = F.[FamiliaId]
    WHERE F.[MunicipioId] = @MunicipioId
      AND P.[PersonaActivo] = 1; 
    RETURN ISNULL(@Cantidad, 0);
END;
GO

-- Función devolver Cantidad de Altas de Personas por Mes
CREATE FUNCTION fn_CantAltasMes
(
    @Periodo INT
)
RETURNS INT
AS
BEGIN
    DECLARE @TotalAltas INT;
    SELECT @TotalAltas = COUNT(NP.[PersonaId])
    FROM [Novedad] N
    INNER JOIN [NovedadPersona] NP ON N.[NovedadId] = NP.[NovedadId]
    WHERE N.[NovedadPeriodo] = @Periodo
      AND NP.[NovedadPersonaTipo] = 'ALT';
    RETURN ISNULL(@TotalAltas, 0);
END;
GO

-- Procedimientos Almacenados

-- Procedimiento almacenado calcular la Cantidad Total de Beneficiarios
CREATE PROCEDURE sp_CantidadTotalBeneficiarios
    @Total INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT @Total = COUNT([PersonaId])
    FROM [Persona];
END;
GO

-- Procedimiento almacenado calcular la Cantidad de Beneficiarios por Grupo Etario
CREATE PROCEDURE sp_CantidadBeneficiariosPorGrupoEtario
 AS
BEGIN
    SET NOCOUNT ON;
    SELECT 
        E.[EtarioNombre] AS GrupoEtario,
        COUNT(P.[PersonaId]) AS CantidadPersonas
    FROM [Etario] E
    LEFT JOIN [Persona] P ON E.[EtarioId] = P.[EtarioId]
    GROUP BY E.[EtarioNombre], E.[EtarioId];
END;
GO

-- Procedimiento almacenado calcular la Cantidad de Beneficiarios por Genero
CREATE PROCEDURE sp_CantidadBeneficiariosPorGenero
AS
BEGIN
    SET NOCOUNT ON;
    SELECT 
        CASE [PersonaSexo]
            WHEN 'M' THEN 'Masculino'
            WHEN 'F' THEN 'Femenino'
            ELSE 'Otro/No especificado'
        END AS Genero,
        COUNT([PersonaId]) AS Cantidad
    FROM [Persona]
    GROUP BY [PersonaSexo];
END;
GO

-- Procedimiento almacenado calcular la Cantidad de Beneficiarios por Localidad
CREATE PROCEDURE sp_CantidadBeneficiariosPorLocalidad
AS
BEGIN
    SET NOCOUNT ON;
    SELECT 
        L.[LocalidadNombre] AS Localidad,
        COUNT(P.[PersonaId]) AS CantidadBeneficiarios
    FROM [Localidad] L
    INNER JOIN [Familia] F ON L.[LocalidadId] = F.[FamiliaLocalidadId]
    INNER JOIN [Persona] P ON F.[FamiliaId] = P.[FamiliaId]
    GROUP BY L.[LocalidadNombre], L.[LocalidadId]
    ORDER BY CantidadBeneficiarios DESC;
END;
GO

-- Procedimiento almacenado calcular el Porcentaje de Beneficiarios que cumplieron los Criterios de Inclusión
CREATE PROCEDURE sp_PorcentajeBeneficiariosCumplieronCriteriosInclusion
    @PorcentajeTotal DECIMAL(5,2) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @TotalPersonas INT;
    DECLARE @PersonasConCriterio INT;
    SELECT @TotalPersonas = COUNT(*) FROM [Persona];
    SELECT @PersonasConCriterio = COUNT(DISTINCT [PersonaId]) 
    FROM [PersonaCriterio] 
    WHERE [PersonaCriterioActivo] = 1;
    IF @TotalPersonas > 0
        SET @PorcentajeTotal = (@PersonasConCriterio * 100.0) / @TotalPersonas;
    ELSE
        SET @PorcentajeTotal = 0;
    SELECT 
        @PorcentajeTotal AS PorcentajeCumplimiento;
END;
GO

-- Procedimiento almacenado calcular el Monto Total Asignado de un Padrón por Período
CREATE PROCEDURE sp_MontoTotalAsignado
    @Periodo INT,
    @MontoTotal MONEY OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT @MontoTotal = SUM(PP.[PadronPersonaMonto])
    FROM [Padron] P
    INNER JOIN [PadronPersona] PP ON P.[PadronId] = PP.[PadronId]
    WHERE P.[PadronPeriodo] = @Periodo;
    IF @MontoTotal IS NULL
        SET @MontoTotal = 0;
    SELECT 
        @MontoTotal AS MontoTotalAsignado;
END;
GO

-- Procedimiento almacenado calcular el Monto Total de Transacciones por rango
CREATE PROCEDURE sp_MontoTotalTransacciones
    @FechaInicio DATETIME,
    @FechaFin DATETIME,
    @MontoTotal MONEY OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT @MontoTotal = SUM([TransaccionMonto])
    FROM [Transaccion]
    WHERE [TransaccionFecha] BETWEEN @FechaInicio AND @FechaFin;
    IF @MontoTotal IS NULL
        SET @MontoTotal = 0;
    SELECT 
        @MontoTotal AS MontoTotal;
END;
GO

-- Procedimiento almacenado calcular la Cantidad Total de Transacciones por rango
CREATE PROCEDURE sp_CantidadTransaccionesPorRango
    @FechaInicio DATETIME,
    @FechaFin DATETIME,
    @TotalTransacciones INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT @TotalTransacciones = COUNT([TransaccionCodigo])
    FROM [Transaccion]
    WHERE [TransaccionFecha] >= @FechaInicio 
      AND [TransaccionFecha] <= @FechaFin;
    IF @TotalTransacciones IS NULL
        SET @TotalTransacciones = 0;
    SELECT 
        @TotalTransacciones AS CantidadDeTransacciones;
END;
GO

-- Procedimiento almacenado calcular el Porcentaje de Mejora por Persona
CREATE PROCEDURE sp_PorcentajeMejoraPersona
    @PersonaId SMALLINT,
    @PorcentajeMejora DECIMAL(5,2) OUTPUT
AS
BEGIN
   SET NOCOUNT ON;
   DECLARE @VulnerabilidActivas INT;
   DECLARE @VulnerabilidadTotales INT;
   DECLARE @VulnerabilidadSuperadas INT;
   SET @VulnerabilidadActivas = dbo.fn_CantVulPerso(@PersonaId);
   SELECT @VulnerabilidadTotales = COUNT(*)
       FROM [PersonaVulnerabilidad]
       WHERE [PersonaId] = @PersonaId;
   SET @VulnerabilidadSuperadas = @VulnerabilidadTotales - @VulnerabilidadActivas;
   IF @VulnerabilidadTotales > 0
      BEGIN SET @PorcentajeMejora = (@VulnerabilidadSuperadas * 100.0) / @VulnerabilidadTotales;
      END
      ELSE
      BEGIN
        SET @PorcentajeMejora = 0.00;
      END
      SELECT 
        @PersonaId AS PersonaId,
        @VulnerabilidadTotales AS TotalHistorico,
        @VulnerabilidadActivas AS TotalActivas,
        @VulnerabilidadSuperadas AS TotalSuperadas,
        @PorcentajeMejora AS PorcentajeMejora;
END;
GO

-- Procedimiento almacenado calcular Promedio de Permanencia en Programa
CREATE PROCEDURE sp_PromedioPermanenciaPrograma
    @ProgramaId SMALLINT,
    @PromDias DECIMAL(10,2) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @TotalDias SUM(INT);
    DECLARE @CantidadPersonas INT;
    SELECT @CantidadPersonas = COUNT(*)
    FROM [ProgramaPersona]
    WHERE [ProgramaId] = @ProgramaId;
    SELECT @TotalDias = SUM(dbo.fn_ CantDiaPerm ([PersonaId], [ProgramaId]))
    FROM [ProgramaPersona]
    WHERE [ProgramaId] = @ProgramaId;
    IF @CantidadPersonas > 0
    BEGIN
        SET @PromDias = CAST(@TotalDias AS DECIMAL(10,2)) / @CantidadPersonas;
    END
    ELSE
    BEGIN
        SET @PromDias = 0;
    END
  SELECT 
        PR.ProgramaNombre,
        dbo.fn_FechaHoy() AS FechaConsulta,
        @CantidadPersonas AS BeneficiariosTotales,
        @PromDias AS PromedioDiasPermanencia
    FROM [Programa] PR
    WHERE PR.ProgramaId = @ProgramaId;
END;
GO

-- Procedimiento almacenado calcular Cantidad de Factores por Persona
CREATE PROCEDURE sp_CantidadFactores
    @PersonaId INT,
    @TotalFactores INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT @TotalFactores = COUNT(*)
    FROM [PersonaFactor]
    WHERE [PersonaId] = @PersonaId AND [PersonaFactorActivo] = 1;
    IF @TotalFactores IS NULL
        SET @TotalFactores = 0;
    SELECT 
        P.[PersonaNombre],
        @TotalFactores AS CantidadFactoresActivos
    FROM [Persona] P
    WHERE P.[PersonaId] = @PersonaId;
END;
GO

-- Procedimiento almacenado calcular el Costo Operativo Mensual
CREATE PROCEDURE sp_CostoOperativoMensual
    @Anio INT,
    @Mes INT,
    @CostoTotal MONEY OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT @CostoTotal = SUM([OperativoMonto])
    FROM [Operativo]
    WHERE YEAR([OperativoFecha]) = @Anio
      AND MONTH([OperativoFecha]) = @Mes
      AND [OperativoActivo] = 1;
    IF @CostoTotal IS NULL
        SET @CostoTotal = 0;
    SELECT 
        @Anio AS [Año],
        @Mes AS [Mes],
        @CostoTotal AS [CostoTotalOperativo];
END;
GO

-- Procedimiento almacenado calcular la Cantidad de Personas con más de un alta activa en Programas
CREATE PROCEDURE sp_CantidadPersonasMultiProgramaActivo
    @TotalPersonas INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    WITH PersonasMultiples AS (
        SELECT [PersonaId]
        FROM [ProgramaPersona]
        WHERE [ProgramaPersonaActivo] = 1
        GROUP BY [PersonaId]
        HAVING COUNT([ProgramaId]) > 1
    )
    SELECT @TotalPersonas = COUNT(*) 
    FROM PersonasMultiples;
    SELECT 
        P.[PersonaId],
        P.[PersonaNombre],
        COUNT(PP.[ProgramaId]) AS CantidadProgramasActivos
    FROM [Persona] P
    INNER JOIN [ProgramaPersona] PP ON P.[PersonaId] = PP.[PersonaId]
    WHERE PP.[ProgramaPersonaActivo] = 1
    GROUP BY P.[PersonaId], P.[PersonaNombre]
    HAVING COUNT(PP.[ProgramaId]) > 1
    ORDER BY CantidadProgramasActivos DESC;
END;
GO

-- Procedimiento almacenado calcular el Nivel de Satisfacción Promedio
CREATE PROCEDURE sp_NivelSatisfaccionPromedio
    @ProgramaId SMALLINT,
    @Periodo INT,
    @Promedio DECIMAL(5,2) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @SumaTotal BIGINT;
    DECLARE @TotalPersonas INT;
    SET @SumaTotal = dbo.fn_SumMesSatPersoProg (@ProgramaId, @Periodo);
    SET @TotalPersonas = dbo.fn_CantSatPersoProg (@ProgramaId, @Periodo);
    IF @TotalPersonas > 0
    BEGIN
        SET @Promedio = CAST (@SumaTotal AS DECIMAL (10,2)) / @TotalPersonas;
    END
    ELSE
    BEGIN
        SET @Promedio = 0.00;
    END
    SELECT 
        P.ProgramaNombre,
        @Periodo AS Periodo,
        @TotalPersonas AS CantidadEncuestados,
        @SumaTotal AS PuntajeTotal,
        @Promedio AS NivelSatisfaccionPromedio
    FROM [Programa] P
    WHERE P.ProgramaId = @ProgramaId;
END;
GO

-- Procedimiento almacenado calcular el Promedio de Altas Mensuales por Municipio
CREATE PROCEDURE sp_PromedioAltasMensualesPorMunicipio
    @MunicipioId SMALLINT,
    @Anio INT,
    @PromedioMensual DECIMAL (10,2) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @SumaAltas INT = 0;
    DECLARE @MesActual INT = 1;
    DECLARE @PeriodoAux INT;
    DECLARE @TotalPersonasActivas INT;
    SET @TotalPersonasActivas = dbo.fn_CantAltasMesMuni(@MunicipioId, (@PeriodoAux);
    WHILE @MesActual <= 12
    BEGIN
        SET @PeriodoAux = (@Anio * 100) + @MesActual;
        SET @SumaAltas = @SumaAltas + dbo.fn_CantAltasMes(@PeriodoAux); 
        SET @MesActual = @MesActual + 1;
    END
    SET @PromedioMensual = CAST (@SumaAltas AS DECIMAL (10,2)) / 12.0;
    SELECT 
        M.MunicipioNombre,
        @Anio AS [AñoConsultado],
        @TotalPersonasActivas AS [PoblacionActivaActual],
        @SumaAltas AS [TotalAltasAnuales],
        @PromedioMensual AS [PromedioAltasMensuales]
    FROM [Municipio] M
    WHERE M.MunicipioId = @MunicipioId;
END;
GO

-- Procedimiento almacenado calcular la Cantidad de Bajas Mensuales por Municipio
CREATE PROCEDURE sp_CantidadBajasPorPeriodoMunicipio
    @MunicipioId SMALLINT,
    @Periodo INT,
    @CantidadBajas INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @CantidadBajas = dbo.fn_CantBajasMesMuni (@MunicipioId, @Periodo);
    SELECT 
        M.MunicipioNombre,
        @CantidadBajas AS [TotalAltasAnuales]
    FROM [Municipio] M
    WHERE M.MunicipioId = @MunicipioId;
END;
GO

-- Procedimiento almacenado calcular el Porcentaje de Crecimiento por Municipio
CREATE PROCEDURE sp_CalcularCrecimientoMunicipal
    @MunicipioId SMALLINT,
    @Periodo INT,
    @PorcentajeCrecimiento DECIMAL (5,2) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Altas INT;
    DECLARE @Bajas INT;
    DECLARE @TotalActual INT;
    DECLARE @DiferenciaNeto INT; 
    SET @Altas = dbo.fn_CantAltasMes(@Periodo); 
    SET @Bajas = dbo.fn_CantBajasMesMuni (@MunicipioId, @Periodo);
    SET @TotalActual = dbo.fn_CantActivasMesMuni(@MunicipioId);
    SET @DiferenciaNeto = @Altas - @Bajas;
    IF @TotalActual > 0
    BEGIN
        SET @PorcentajeCrecimiento = (@DiferenciaNeto * 100.0) / @TotalActual;
    END
    ELSE
    BEGIN
        SET @PorcentajeCrecimiento = 0.00;
    END
    SELECT 
        M.MunicipioNombre,
        @Periodo AS Periodo,
        @Altas AS AltasPeriodo,
        @Bajas AS BajasPeriodo,
        @DiferenciaNeto AS VariacionNeta,
        @TotalActual AS PoblacionTotal,
        @PorcentajeCrecimiento AS PorcentajeCrecimiento
    FROM [Municipio] M
    WHERE M.MunicipioId = @MunicipioId;
END;
GO
