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
    SET BASECFG=base_config_gpu.cfg
) ELSE (
    SET BASECFG=base_config_cpu.cfg
)

echo ============================================
echo Training mode: %MODE%
echo Base config: %BASECFG%
echo ============================================

REM Prepare data
python prepare_data.py

REM Fill config
python -m spacy init fill-config %BASECFG% config.cfg

REM Debug data
python -m spacy debug data config.cfg

REM Preliminary evaluation of base model
echo --------------------------------------------
echo Evaluating base model BEFORE fine-tuning...
echo --------------------------------------------
python -m spacy evaluate it_core_news_lg docbins/test.spacy --output models/%MODE%/pretrain_results.json
echo Base model evaluation saved to models/%MODE%/pretrain_results.json

REM Train
echo --------------------------------------------
echo Starting fine-tuning training...
echo --------------------------------------------
python -m spacy train config.cfg --output models/%MODE%

REM Evaluate trained model
echo --------------------------------------------
echo Evaluating fine-tuned model...
echo --------------------------------------------
python -m spacy evaluate models/%MODE%/model-best docbins/test.spacy --output models/%MODE%/model-best/test_results.json
echo Fine-tuned model evaluation saved to models/%MODE%/model-best/test_results.json

pause
