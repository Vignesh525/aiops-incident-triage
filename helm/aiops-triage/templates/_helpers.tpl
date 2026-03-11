{{- define "aiops-triage.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "aiops-triage.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := include "aiops-triage.name" . -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{- define "aiops-triage.labels" -}}
app.kubernetes.io/name: {{ include "aiops-triage.name" . }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "aiops-triage.selectorLabels" -}}
app.kubernetes.io/name: {{ include "aiops-triage.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "aiops-triage.apiName" -}}
{{- printf "%s-api" (include "aiops-triage.fullname" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "aiops-triage.workerName" -}}
{{- printf "%s-worker" (include "aiops-triage.fullname" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "aiops-triage.configName" -}}
{{- printf "%s-config" (include "aiops-triage.fullname" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "aiops-triage.secretName" -}}
{{- if .Values.existingSecret -}}
{{- .Values.existingSecret -}}
{{- else -}}
{{- printf "%s-secrets" (include "aiops-triage.fullname" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
