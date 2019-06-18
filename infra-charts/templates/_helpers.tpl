{{/*
Copyright 2019 Nokia

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/}}
{{- define "caas.protocol_parser" }}
{{- $url :=  regexSplit ":" . -1 }}
       protocol {{ index $url 0 }}
{{- end }}
{{- define "caas.scheme_parser" }}
{{- $url :=  regexSplit ":" . -1 }}
       scheme {{ index $url 0 }}
{{- end }}
{{- define "caas.url_parser" }}
{{- $url :=  regexSplit ":" . -1 }}
{{- $just_url :=  index $url 1 }}
{{- $just_url :=  regexSplit "\\/\\/" $just_url -1 }}
       host {{ index $just_url 1 }}
       port {{ index $url 2 }}
{{- end }}
