@echo off
REM ============================
REM Usage: train.bat [cpu|gpu]
REM Example: train.bat gpu
REM ============================

IF "%1"=="" (
    echo Please specify mode: cpu or gpu
    exit /b 1
)

SET MODE=%1

REM Choose base config depending on argument
IF /I "%MODE%"=="gpu" (
    SET BASECFG=NER/base_config_gpu.cfg
) ELSE (
    SET BASECFG=NER/base_config_cpu.cfg
)

echo ============================================
echo Training mode: %MODE%
echo Base config: %BASECFG%
echo ============================================

REM Step 1: Prepare data
python NER\\prepare_data.py

REM Step 2: Fill config
python -m spacy init fill-config %BASECFG% config.cfg

REM Step 3: Debug data
python -m spacy debug data config.cfg

REM Step 4: Train
python -m spacy train config.cfg --output NER/models/%MODE%

REM Step 5: Test
python -m spacy evaluate NER/models/%MODE%/model-best NER/docbins/test.spacy --output NER/models/%MODE%/model-best/test_results.json

pause
