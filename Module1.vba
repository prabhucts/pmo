'Rem ##########################################################################################################################################################
'Rem Script/Tool Name : Clarity Worksheet for the ITPR
'Rem Current Version - 3.1 - This version has implementation of the following 2 things:
'Rem 1) Create the ITPR for the Team members
'Rem 2) Create the ITRP fro the Team Leads
'Rem 3) The dump column is not hard coded
'Rem 4) Removing the hard coded SP conversion and using reference for this
'Rem 5) Adding new clarity allocation
'Rem 6) checking the Team worksheet for allocation %
'Rem Previous Version - 3.0
'Rem Version Creation Date: 7/15/2025
'Rem Version Implemention: Nischal Chhetri
'Rem Version Reviewer : Sapna Patel

Rem ##########################################################################################################################################################



Sub RunningCode()
    Dim wsSource As Worksheet
    Dim resultfRow
    Dim uniqueValues As Collection
    Dim cell As Range
    Dim value As Variant
    Dim outputRow As Long
    Dim criteria1, criteria2, criteria3


Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
    ' Set the source and target worksheets
Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
    Set ws_clarity = ThisWorkbook.Sheets("Clarity_team")
    Set ws_clarity_l = ThisWorkbook.Sheets("Clarity_Lead")
    Set ws_ref = ThisWorkbook.Sheets("Reference")
    'Set ws_sum = ThisWorkbook.Sheets("Summary_PI")
    Set ws_US = ThisWorkbook.Sheets("ExtractUS")
    Set ws_fea = ThisWorkbook.Sheets("RawFeature")
    Set ws_epic = ThisWorkbook.Sheets("RawEpic")
    Set ws_sum1 = ThisWorkbook.Sheets("Summary")
    Set ws_Teams = ThisWorkbook.Sheets("Team Members")
    Set ws_clarity1 = ThisWorkbook.Sheets("Clarity_Sprint")
    Set ws_itpr = ThisWorkbook.Sheets("ITPR Owner")
    Set ws_defect = ThisWorkbook.Sheets("ExtractDefect")


'Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
'Reading the User story dump excel file
'Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
    lastRow_ws_US = ws_US.Cells(ws_US.Rows.count, 1).End(-4162).Row
    lastColumn_ws_US = ws_US.Cells(1, ws_US.Columns.count).End(-4159).Column
    ' Loop through the columns in the first row to find the heading - feature
        Headerfound = False
        Feat = "Feature"
        For x = 1 To lastColumn_ws_US
            If ws_US.Cells(1, x).value = Feat Then
                US_feat_index = x
                Headerfound = True
            Exit For
            End If
        Next
        ' Check if the heading was found
        If Not Headerfound Then
            MsgBox "Feature Not Found, check User story dump"
            Exit Sub
        End If
        'msgbox US_feat_index
    ' Loop through the columns in the first row to find the heading - Project for team name
        Headerfound = False
        Pro = "Project"
        For x = 1 To lastColumn_ws_US
            If ws_US.Cells(1, x).value = Pro Then
            US_Team_index = x
            Headerfound = True
            Exit For
            End If
        Next
        ' Check if the heading was found
        If Not Headerfound Then
            MsgBox "Team Name Not Found, check User story dump"
            Exit Sub
        End If

    ' Loop through the columns in the first row to find the heading - Plan estimate for user story
        Headerfound = False
        Pl_est = "Plan Estimate"
        For x = 1 To lastColumn_ws_US
            If ws_US.Cells(1, x).value = Pl_est Then
            US_estimate_index = x
            Headerfound = True
            Exit For
            End If
        Next


    ' Loop through the columns in the first row to find the heading - Sprint for user story
        Headerfound = False
        P_Sp = "Iteration"
        For x = 1 To lastColumn_ws_US
            If ws_US.Cells(1, x).value = P_Sp Then
            US_Sprint_index = x
            Headerfound = True
            Exit For
            End If
        Next

    ' Loop through the columns in the first row to find the formated id user story
        Headerfound = False
        US_ID = "Formatted ID"
        For x = 1 To lastColumn_ws_US
            If ws_US.Cells(1, x).value = US_ID Then
            US_formatted_index = x
            Headerfound = True
            Exit For
            End If
        Next


'Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
'Reading the Feature dump excel file
'Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
    lastRow_ws_fea = ws_fea.Cells(ws_fea.Rows.count, 1).End(-4162).Row
    lastColumn_ws_fea = ws_fea.Cells(1, ws_fea.Columns.count).End(-4159).Column
    ' Loop through the columns in the first row to find the heading - feature
        Headerfound = False
        Feat = "Formatted ID"
        For x = 1 To lastColumn_ws_fea
            If ws_fea.Cells(1, x).value = Feat Then
                Feat_feat_index = x
                Headerfound = True
            Exit For
            End If
        Next
        'MsgBox Feat_feat_index
        ' Check if the heading was found
        If Not Headerfound Then
            MsgBox "Feature Not Found, check Feature dump"
            Exit Sub
        End If
        'msgbox US_feat_index
    ' Loop through the columns in the first row to find the heading - Project for team name
        Headerfound = False
        Pro = "Parent"
        For x = 1 To lastColumn_ws_fea
            If ws_fea.Cells(1, x).value = Pro Then
            Feat_Epic_index = x
            Headerfound = True
            Exit For
            End If
        Next
        ' Check if the heading was found
        If Not Headerfound Then
            MsgBox "Epic Not Found, check Feature dump"
            Exit Sub
        End If

'Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
'Reading the Epic dump excel file
'Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
    lastRow_ws_epic = ws_epic.Cells(ws_epic.Rows.count, 1).End(-4162).Row
    lastColumn_ws_epic = ws_epic.Cells(1, ws_epic.Columns.count).End(-4159).Column
    ' Loop through the columns in the first row to find the heading - feature
        Headerfound = False
        Feat = "Formatted ID"
        For x = 1 To lastColumn_ws_epic
            If ws_epic.Cells(1, x).value = Feat Then
                Epic_epic_index = x
                Headerfound = True
            Exit For
            End If
        Next
        'MsgBox Feat_feat_index
        ' Check if the heading was found
        If Not Headerfound Then
            MsgBox "Epic Not Found, check Epic dump"
            Exit Sub
        End If
        'msgbox US_feat_index
    ' Loop through the columns in the first row to find the heading - Project for team name
        Headerfound = False
        Pro = "Parent"
        For x = 1 To lastColumn_ws_epic
            If ws_epic.Cells(1, x).value = Pro Then
            Epic_Itpr_index = x
            Headerfound = True
            Exit For
            End If
        Next
        ' Check if the heading was found
        If Not Headerfound Then
            MsgBox "ITPR Not Found, check Epic dump"
            Exit Sub
        End If


'Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
'Reading the Defect dump excel file
'Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
    lastRow_ws_defect = ws_defect.Cells(ws_defect.Rows.count, 1).End(-4162).Row
    lastColumn_ws_defect = ws_defect.Cells(1, ws_defect.Columns.count).End(-4159).Column
    ' Loop through the columns in the first row to find the heading - feature
        Headerfound = False
        Users = "Requirement"
        For x = 1 To lastColumn_ws_defect
            If ws_defect.Cells(1, x).value = Users Then
                Defect_US_index = x
                Headerfound = True
            Exit For
            End If
        Next
        ' Check if the heading was found
        If Not Headerfound Then
            MsgBox "User story Not Found, check Defect dump"
            Exit Sub
        End If

    ' Loop through the columns in the first row to find the heading - Project for team name
        Headerfound = False
        Pro = "Project"
        For x = 1 To lastColumn_ws_defect
            If ws_defect.Cells(1, x).value = Pro Then
            Defect_Team_index = x
            Headerfound = True
            Exit For
            End If
        Next
                ' Check if the heading was found
        If Not Headerfound Then
            MsgBox "Project or team Not Found, check Defect dump"
            Exit Sub
        End If



    ' Loop through the columns in the first row to find the heading - Plan estimate for user story
        Headerfound = False
        Pl_est = "Plan Estimate"
        For x = 1 To lastColumn_ws_defect
            If ws_defect.Cells(1, x).value = Pl_est Then
            Defect_estimate_index = x
            Headerfound = True
            Exit For
            End If
        Next

                ' Check if the heading was found
        If Not Headerfound Then
            MsgBox "Plan estimate Not Found, check Defect dump"
            Exit Sub
        End If



    ' Loop through the columns in the first row to find the heading - Sprint for user story
        Headerfound = False
        P_Sp = "Iteration"
        For x = 1 To lastColumn_ws_defect
            If ws_defect.Cells(1, x).value = P_Sp Then
            Defect_Sprint_index = x
            Headerfound = True
            Exit For
            End If
        Next



    ' Loop through the columns in the first row to find the heading - Sprint for user story
        Headerfound = False
        Protfolio_Sp = "Portfolio Item"
        For x = 1 To lastColumn_ws_defect
            If ws_defect.Cells(1, x).value = Protfolio_Sp Then
            Defect_protofolio_index = x
            Headerfound = True
            Exit For
            End If
        Next

                ' Check if the heading was found
        If Not Headerfound Then
            MsgBox "Defect Portfolio Item not found, check Defect dump"
            Exit Sub
        End If




Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
    ' setting up the header for summary worksheet
Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================

    ws_sum1.Cells.ClearContents
    ws_sum1.Cells(1, 1).value = "Team"
    ws_sum1.Cells(1, 2).value = "Features"
    ws_sum1.Cells(1, 3).value = "EPIC"
    ws_sum1.Cells(1, 4).value = "ITPR"
    ws_sum1.Cells(1, 5).value = "Total US Point"
    ws_sum1.Cells(1, 6).value = "Total Hours"
    ws_sum1.Cells(1, 7).value = "#Per Week hours"

    'ws_sum1.Cells(1, 8).value = ws_ref.Cells(3, 14).value
    'ws_sum1.Cells(1, 9).value = ws_ref.Cells(4, 14).value
    'ws_sum1.Cells(1, 10).value = ws_ref.Cells(5, 14).value
    'ws_sum1.Cells(1, 11).value = ws_ref.Cells(6, 14).value
    'ws_sum1.Cells(1, 12).value = ws_ref.Cells(7, 14).value
    'ws_sum1.Cells(1, 13).value = ws_ref.Cells(8, 14).value
    'getting all sprints for the summary
    columnNumber = 13
    ' Loop through the rows in the specified column
    For i = 1 To ws_ref.UsedRange.Rows.count
        If Not IsEmpty(ws_ref.Cells(i, columnNumber).value) Then
            columnLength = columnLength + 1
        End If
    Next
    'MsgBox columnLength
    a = 8
    For i = 3 To columnLength
        ws_sum1.Cells(1, a).value = ws_ref.Cells(i, 13).value
        a = a + 1
    Next i



Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
    ' 'Removing all filter from the worksheets before running the code
Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
    For Each ws In ThisWorkbook.Worksheets
        ' Check if AutoFilter is enabled for the worksheet
        If ws.AutoFilterMode Then
            ' Check if a filter is actually applied (rows hidden)
            If ws.FilterMode Then
                ' Show all data, effectively clearing the filter
                ws.ShowAllData
            End If
        End If
    Next ws



    'Set ws1 = ThisWorkbook.Sheets("Sheet2") ' Change to your sheet name
    'Set ws2 = ThisWorkbook.Sheets("Sheet3") ' Change to your sheet name
    Set uniqueValues = New Collection
    ' Find the last row in Ws1 and Ws2
    lastRow_ws_ref = ws_ref.Cells(ws_ref.Rows.count, 1).End(-4162).Row ' -4162 is equivalent to xlUp
    lastRow_ws_US = ws_US.Cells(ws_US.Rows.count, 1).End(-4162).Row
    lastRow_ws_fea = ws_fea.Cells(ws_fea.Rows.count, 1).End(-4162).Row
    lastRow_ws_Teams = ws_Teams.Cells(ws_Teams.Rows.count, 1).End(-4162).Row
    lastRow_ws_itpr = ws_itpr.Cells(ws_itpr.Rows.count, 1).End(-4162).Row
    lastRow_ws_defect = ws_defect.Cells(ws_defect.Rows.count, 1).End(-4162).Row

Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
    '  'Creating the reference data based on team member sheet
Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
    Set uniqueResults = CreateObject("Scripting.Dictionary")
        resultfRow = 2
        ws_ref.Cells(resultfRow - 1, 1).value = "Team"
        For i = 2 To lastRow_ws_Teams  'as from the team member All teams is causing blank iTP
            team = ws_Teams.Cells(i, 1).value
            'MsgBox team
            If Not uniqueResults.Exists(team) Then
                uniqueResults.Add team, Nothing
            End If
        Next i
        For Each team In uniqueResults.Keys
            ws_ref.Cells(resultfRow, 1).value = team
            criteria1 = team
            ' Call the CountIfs function
            result = CountIfs1(ws_Teams, lastRow_ws_Teams, criteria1, 1) 'count of team members
            ws_ref.Cells(resultfRow, 2).value = result
            role = ws_Teams.Cells(i, 5).value
            criteria2 = "Product"
                result1 = CountIfs2(ws_Teams, lastRow_ws_Teams, criteria1, 1, criteria2, 5) 'count of team members
                ws_ref.Cells(resultfRow, 3).value = result1

            'Checking the Rally allocation of each team and getting the value for Summary calculation
            rally_all = SumIfs10(ws_Teams, lastRow_ws_Teams, 8, criteria1, 1)
            'MsgBox rally_all
            rally_all = rally_all / 100
              ws_ref.Cells(resultfRow, 5).value = rally_all
            'criteria2 = 50
             '   result2_1 = CountIfs2(ws_Teams, lastRow_ws_Teams, criteria1, 1, criteria2, 8) 'count of team members

                'result2 = result2_1 + result2_2
               ' ws_ref.Cells(resultfRow, 4).value = result2
               ' ws_ref.Cells(resultfRow, 5).value = result - result1 - (result2 / 2)





            resultfRow = resultfRow + 1



        Next


Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
    ' creating the summary worksheet data based on the User story dump
Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
    'Getting all the feature based on the team name
    resultfRow = 2
    For i = 2 To lastRow_ws_ref - 1
        searchvalue = ws_ref.Cells(i, 1).value ' Get the team from user story dump
        'resultValue = "Not Found" ' Default value if not found
        'MsgBox searchvalue
        ws_sum1.Cells(resultfRow, 1).value = searchvalue
        ' Initialize resultRow for each searchValue
        'resultRow = 2 ' Start writing results from row 2 in ws_sum1
        ' Clear the dictionary for each searchValue
        uniqueResults.RemoveAll
    ' Loop through each value in Ws2 to find a match
        For j = 2 To lastRow_ws_US
            'MsgBox ws_US.Cells(j, 11).value
            If ws_US.Cells(j, US_Team_index).value = searchvalue Then
                resultfeatValue = ws_US.Cells(j, US_feat_index).value ' Get the corresponding feature from column B
                'MsgBox resultfeatValue
                ' Add the result to the dictionary (only unique values)
                If Not uniqueResults.Exists(resultfeatValue) Then
                    uniqueResults.Add resultfeatValue, Nothing
                End If
            End If
            ' Write unique results back to ws_sum1
        Next j
            'resultfRow = i ' Start writing results from row 2 in ws_sum1
            For Each resultfeatValue In uniqueResults.Keys
                'MsgBox resultfRow
                ws_sum1.Cells(resultfRow, 2).value = resultfeatValue ' Write the unique result to the next column
                ws_sum1.Cells(resultfRow, 1).value = searchvalue
                'MsgBox searchvalue
                    'Vlook for epic using feature
                    resultfeature = Mid(resultfeatValue, 9, 7)
                    'MsgBox resultfeature
                    'VLookup(lookupValue, lookupSheet, returnColumn, searchColumn)
                    SearchEpic = VLookup(resultfeature, ws_fea, Feat_Epic_index, Feat_feat_index)
                    'MsgBox SearchEpic
                    If Not IsNull(SearchEpic) Then
                        ws_sum1.Cells(resultfRow, 3).value = SearchEpic
                            ' trimming the EPIC Find the position of the first colon
                            'MsgBox SearchEpic
                            colonPosition = InStr(SearchEpic, ":")
                            ' Check if the colon was found
                            If colonPosition > 0 Then
                            ' Extract the substring from the start to the position before the colon
                                resultString = Mid(SearchEpic, 6, colonPosition - 6)
                                'MsgBox resultString
                                searchItpr = VLookup(resultString, ws_epic, Epic_Itpr_index, Epic_epic_index)
                                'MsgBox searchItpr
                                'Checking for planned vs unplanned ITPR or not applicable
                                ws_sum1.Cells(resultfRow, 4).value = searchItpr 'returning the ITPR based on epic

                            End If
                  Else
                        ws_sum1.Cells(resultfRow, 3).value = "No Epic"
                        ws_sum1.Cells(resultfRow, 4).value = "No ITPR"
                    End If
                    criteria1 = resultfeatValue 'Change to your actual criteria
                    criteria2 = searchvalue ' Change to your actual criteria
                    'Extracting US story point and hours , based on feature and team
                    sumResult = SumIfs(ws_US, lastRow_ws_US, US_estimate_index, criteria1, US_feat_index, criteria2, US_Team_index)
                    'MsgBox sumResult
                    'checking if this feature has any defect and getting estimate
                    defect_estimate = defectestimate(resultfeatValue, searchvalue, ws_defect, ws_sum1, ws_US, ws_itpr, Defect_US_index, Defect_Team_index, US_feat_index, US_Team_index, Defect_estimate_index, US_formatted_index, Defect_protofolio_index)
                    'defect_l3_estimate = defectl3estimate(resultfeatValue, searchvalue, ws_defect, ws_sum1, ws_itpr)
                    sumResult = sumResult + defect_estimate
                    'MsgBox sumResult
                    ws_sum1.Cells(resultfRow, 5).value = sumResult
                    'ws_sum1.Cells(resultfRow, 6).value = sumResult * 16    'Harded code 16 per story point
                    'MsgBox sumResult
                    'MsgBox searchvalue
                    Sp_Hours = VLookup(searchvalue, ws_ref, 6, 1)
                    'MsgBox Sp_Hours
                    ws_sum1.Cells(resultfRow, 6).value = sumResult * Sp_Hours

                    'MsgBox searchvalue
                    Sum = CalculateHours(sumResult, searchvalue, ws_ref, weeks, Sp_Hours)
                    'MsgBox Sum
                    ws_sum1.Cells(resultfRow, 7).value = Sum

                    'Extracting US story point and hours , based on feature and team & sprint
                    lastColumn_ws_ref = ws_ref.UsedRange.Columns.count
                    For k = 8 To lastColumn_ws_ref
                        sprint = ws_sum1.Cells(1, k).value
                        'MsgBox sprint
                        criteria3 = sprint
                        sumResult = SumIfs4(ws_US, lastRow_ws_US, US_estimate_index, criteria1, US_feat_index, criteria2, US_Team_index, criteria3, US_Sprint_index)
                        'Sum = CalculateHours(sumResult, searchvalue, ws_ref)
                        ws_sum1.Cells(resultfRow, k).value = sumResult 'SP for user story

                        'SumIfs4(dataSheet, lastRow, sumColumn, criteria1, criteriaColumn1, criteria2, criteriaColumn2, criteria3, criteriaColumn3)
                    Next k
                    'getting defect SP
            resultfRow = resultfRow + 1
            Next
    Next i

Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
    ' Updating the the summary worksheet data based on the defect dump - l3 defect
Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
    'l3 defect estimate
    lastRow_ws_defect = ws_defect.Cells(ws_defect.Rows.count, 1).End(-4162).Row
    lastRow_ws_sum1 = ws_sum1.Cells(ws_sum1.Rows.count, 1).End(-4162).Row
    'MsgBox "inside l3 defect"
    For i = 2 To lastRow_ws_ref - 1
        searchteam = ws_ref.Cells(i, 1).value
        'MsgBox searchteam
        Sp_Hours = ws_ref.Cells(i, 6).value
        criteria1 = searchteam
        criteria2 = blank
        criteria3 = blank
        team_defect_effort = SumIfs4(ws_defect, lastRow_ws_defect, Defect_estimate_index, criteria1, Defect_Team_index, criteria2, Defect_US_index, criteria3, Defect_protofolio_index)
        lastcolumn_ws_sum1 = ws_sum1.UsedRange.Columns.count
        'MsgBox team_defect_effort
        If team_defect_effort > 0 Then
            'MsgBox team_defect_effort
            stringa = "L3 defect"
            ip = VLookup(stringa, ws_itpr, 2, 4)
            'MsgBox ip
            th = VLookup(stringa, ws_itpr, 1, 4)
            'MsgBox th
            itpr_x = "Theme " & th & ": " & ip
            'MsgBox itpr_x
            For j = 2 To lastRow_ws_sum1
                If ws_sum1.Cells(j, 1).value = searchteam And ws_sum1.Cells(j, 4).value = itpr_x Then
                    eff = ws_sum1.Cells(j, 5).value
                    'MsgBox eff
                    US_defect_user_effort = eff + team_defect_effort
                    ws_sum1.Cells(j, 5).value = US_defect_user_effort
                    'MsgBox US_defect_user_effort
                    Us_hours = ws_sum1.Cells(j, 6).value
                    defect_hours = team_defect_effort * Sp_Hours
                    ws_sum1.Cells(j, 6).value = Us_hours + defect_hours

                    sprint = ws_defect.Cells(i, Defect_Sprint_index).value
                    'MsgBox sprint
                    For k = 8 To lastcolumn_ws_sum1
                        s_sprint = ws_sum1.Cells(1, k).value
                        'MsgBox S_sprint
                        If s_sprint = sprint Then
                            'MsgBox "sprint matched"
                            eff1 = ws_sum1.Cells(j, k).value
                            'MsgBox eff1
                            final_eff = eff1 + team_defect_effort
                            'MsgBox final_eff
                            ws_sum1.Cells(j, k).value = final_eff
                        End If

                    Next k
                End If
            Next j
      End If
    Next i



Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
    ' Creating the Clarity worksheet based on whole PI SP allocation for team members (no sprint wise)
Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
    'Creating the claritysheet - per PI
    'finished summary, creating clarity for team member
    Sum = ClaritySheet(ws_clarity, ws_ref, ws_Teams, ws_sum1, ws_itpr)
    'Getting the time for each ITPR based on team member assignment
    lastRow_ws_sum1 = ws_sum1.Cells(ws_sum1.Rows.count, 1).End(-4162).Row
    lastRow_ws_clarity = ws_clarity.Cells(ws_clarity.Rows.count, 1).End(-4162).Row
    'MsgBox "here"
    For i = 2 To lastRow_ws_clarity
        itpr = ws_clarity.Cells(i, 2).value
        'MsgBox itpr
        team = ws_clarity.Cells(i, 1).value
        'MsgBox team
        'Getting the estimate for each ITPR for the team
        teammember = ws_clarity.Cells(i, 6).value
        'MsgBox teammember
        criteria1 = itpr 'Search for ITPR
        criteria2 = team 'search for team
        estimate = SumIfs(ws_sum1, lastRow_ws_sum1, 7, criteria1, 4, criteria2, 1)
        'MsgBox estimate
        'Calculating the ITPR estimate based on team member percentage defined
        'MsgBox estimate
        Value1 = VLookup(teammember, ws_Teams, 9, 2)
        'MsgBox Value1
        'percentage = Value1 / 100
        'MsgBox percentage
        estimate = estimate * Value1
        'MsgBox estimate

        'MsgBox estimate
       ' MsgBox estimate
        'lastcolumn_ws_clarity = ws_clarity.Cells(ws_clarity.Columns.Count, 1).End(-4162).Column
        'checking the logic for estimate for ITPR (getting from summary and for core)



        If estimate = 0 Then
            'MsgBox "zero"
            estimate = VLookup(itpr, ws_itpr, 5, 2)
        Else
            estimate = Round(estimate, 0)
            If estimate = 0 Then
                estimate = 1
            Else
                estimate = estimate
            End If
        End If


        lastcolumn_ws_clarity = ws_clarity.UsedRange.Columns.count
        'MsgBox lastcolumn_ws_clarity
        For j = 9 To lastcolumn_ws_clarity
            ws_clarity.Cells(i, j).value = estimate
        'MsgBox estimate
        Next j
    Next i

Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
    ' Creating the Clarity worksheet for the leaders of team based on SP for whole train
Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
    'creating clarity for leaders of team
    Sum = ClaritySheet_l(ws_clarity_l, ws_ref, ws_Teams, ws_sum1, ws_itpr)
    'MsgBox "here in code"
    lastRow_ws_sum1 = ws_sum1.Cells(ws_sum1.Rows.count, 1).End(-4162).Row
    lastRow_ws_clarity_l = ws_clarity_l.Cells(ws_clarity.Rows.count, 1).End(-4162).Row
    lastcolumn_ws_clarity_1 = ws_clarity_l.UsedRange.Columns.count

    'MsgBox lastRow_ws_clarity_l
    For i = 2 To lastRow_ws_clarity_l
        ITPR1 = ws_clarity_l.Cells(i, 2).value
        'MsgBox ITPR1
        Name = ws_clarity_l.Cells(i, 6).value
        team = ws_clarity_l.Cells(i, 1).value
        criteria1 = ITPR1
        team = ws_clarity_l.Cells(i, 1).value
        Value1 = VLookup(team, ws_Teams, 9, 1)
        'MsgBox Value1
        'percentage = Value1 / 100
        'MsgBox percentage
        'MsgBox Value1
        estimate1 = SumIfs2(ws_sum1, lastRow_ws_sum1, 7, criteria1, 4)
        'MsgBox estimate1
        finalestimate1 = estimate1 * Value1
        'MsgBox finalestimate1

        If finalestimate1 = 0 Then
                'MsgBox "zero"
                finalestimate1 = VLookup(ITPR1, ws_itpr, 6, 2)
                'MsgBox finalestimate1
        Else
                finalestimate1 = Round(finalestimate1, 0)
                    If finalestimate1 = 0 Then
                        finalestimate1 = 1
                    Else
                        finalestimate1 = finalestimate1
                    End If

        End If
        'MsgBox finalestimate1

        For j = 9 To lastcolumn_ws_clarity_1
            ws_clarity_l.Cells(i, j).value = finalestimate1
        Next j
    Next i


    'Comparing with the base file
    'Workbooks.Open Filename:=ThisWorkbook.Path & "\Insights and Outreach ITPR Allocations for Q3.xls"
    ' Get the full path of the currently running script
    'scriptPath = WScript.ScriptFullName




    MsgBox "Consolidation of Summary is done"

End Sub

Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================
Rem Fuction name: CalculateHoursPerRes ()
Rem Fuction Arguments: estimate, value, worksheet
'Rem Fuction tasks: Function calculate the hours per week based on user story SP for that week
Rem Creation Date: 07/22/2025
Rem ===================================+++++++++++++++++++++++++++++++++++++++++++++++++++++++++=========================================================

Function CalculateHoursPerRes(estimate, searchvalue, value, ws_ref, Sp_Hours)
    'MsgBox "Inside calculate hours"
    'MsgBox estimate
    'MsgBox value

    Sp_Hours = VLookup(searchvalue, ws_ref, 6, 1)
    teamcount = VLookup(searchvalue, ws_ref, 5, 1)
    'MsgBox teamcount
    'total hours based on estimate for whole team
    totalhours = estimate * Sp_Hours
    If totalhours = 0 Then
        CalculateHoursPerRes = 0
    Else
        'total hours for individual team member
        If teamcount > 0 Then
            totalhours_team = totalhours / teamcount
        Else
            totalhours_team = totalhours
        End If
        'per day hours for individual team member
        hoursperday = totalhours_team / 10
        'MsgBox hoursperday

        If hoursperday > 0 Then
            CalculateHoursPerRes = hoursperday * value
         '   MsgBox CalculateHoursPerRes
        Else
            CalculateHoursPerRes = 0
        End If
        'MsgBox CalculateHoursPerRes
    End If
    'MsgBox CalculateHoursPerRes
    CalculateHoursPerRes = Round(CalculateHoursPerRes, 0)

End Function

Function CalculateHours(sumResult, searchvalue, ws_ref, weeks, Sp_Hours)
    'MsgBox searchvalue
    'no of weeks = 10
    'weeks = 10
    weeks = ws_ref.Range("I5").value
    teamcount = VLookup(searchvalue, ws_ref, 5, 1)
    'MsgBox teamcount
    'Sp_Hours = VLookup(searchvalue, ws_ref, 6, 1)
    'MsgBox Sp_Hours
    'No_of_Sprint = ws_ref.Cells(3, 9)
    sumResult = sumResult * Sp_Hours
    If teamcount > 0 Then
        CalculateHours = sumResult / weeks / teamcount
    Else
        CalculateHours = 0
    End If
    'MsgBox CalculateHours



End Function

Function defectestimate(resultfeatValue, searchvalue, ws_defect, ws_sum1, ws_US, ws_itpr, Defect_US_index, Defect_Team_index, US_feat_index, US_Team_index, Defect_estimate_index, US_formatted_index, Defect_protofolio_index)
    'MsgBox "inside defect estimate"
    'MsgBox resultfeatValue
    lastRow_ws_defect = ws_defect.Cells(ws_defect.Rows.count, 1).End(-4162).Row ' -4162 is equivalent to xlUp
    lastRow_ws_sum1 = ws_sum1.Cells(ws_sum1.Rows.count, 1).End(-4162).Row ' -4162 is equivalent to xlUp
    defectestimate = 0
    For i = 2 To lastRow_ws_defect
        defect = ws_defect.Cells(i, 1).value
        'MsgBox defect
        User_story = ws_defect.Cells(i, Defect_US_index).value
        len_us = Len(ws_defect.Cells(i, 3).value)
        'MsgBox User_story
        team_name = ws_defect.Cells(i, Defect_Team_index).value
        'MsgBox len_US


        'MsgBox User_story
        team_name = ws_defect.Cells(i, Defect_Team_index).value
        defect_protofolio = ws_defect.Cells(i, Defect_protofolio_index).value

        If Not IsNull(defect_protofolio) And Trim(defect_protofolio) <> "" Then
           ' MsgBox "Not null feature for defect "
            'MsgBox defect_protofolio
            If resultfeatValue = defect_protofolio And team_name = searchvalue Then
                    defect_est = ws_defect.Cells(i, Defect_estimate_index).value
                   ' MsgBox defect_est
            Else
                defect_est = 0
            End If

        ElseIf len_us > 0 Then
            'MsgBox "Not null user story"
            'MsgBox User_story
             colonPosition = InStr(User_story, ":")
            'MsgBox colonPosition
            If colonPosition > 0 Then
                'MsgBox "Defect with user story"
                sub_string = Left(User_story, colonPosition - 1)
                'MsgBox sub_string
                fea = VLookup(sub_string, ws_US, US_feat_index, US_formatted_index)
                'fea = VLookup(sub_string, ws_US, 10, 1)
                'Function VLookup(lookupValue, lookupSheet, returnColumn, searchColumn)
                'MsgBox fea
                If resultfeatValue = fea And team_name = searchvalue Then
                    defect_est = ws_defect.Cells(i, Defect_estimate_index).value
                    'MsgBox defect_est
                Else
                    defect_est = 0
                End If
            Else
                'MsgBox "Defect with user story"

            End If


        Else
            defect_est = 0
        End If
        defectestimate = defect_est + defectestimate
        'MsgBox defectestimate
    Next i

        'defectestimate = defect_est + defectestimate
        'MsgBox "Final defect:" & defectestimate


End Function


Function defectl3estimate(resultfeatValue, searchvalue, ws_defect, ws_sum1, ws_itpr)
    stringa = "L3 defect"
    ip = VLookup(stringa, ws_itpr, 2, 4)
    'MsgBox ip
    th = VLookup(stringa, ws_itpr, 1, 4)
    'MsgBox th
    itpr_x = th & ": " & ip
    'MsgBox itpr_x



End Function



Function ClaritySheet(ws_clarity, ws_ref, ws_Teams, ws_sum1, ws_itpr)
    ws_clarity.Cells.ClearContents


    'MsgBox "her in claritysheet"
    Dim uniqueValues As Collection
    i = 1
    ws_clarity.Cells(i, 1).value = "Team"
    ws_clarity.Cells(i, 2).value = "Initiative with THEME"
    ws_clarity.Cells(i, 3).value = "Initiative (Use Dropdown of Current ITPRs)"
    ws_clarity.Cells(i, 4).value = "PMO Owner"
    ws_clarity.Cells(i, 5).value = "Missing from Clarity assingment"
    ws_clarity.Cells(i, 6).value = "Resource Name (in Clarity)"
    ws_clarity.Cells(i, 7).value = "Network ID or email Location"
    ws_clarity.Cells(i, 8).value = "Location"
    'ws_clarity.Cells(i, 9).value = ws_ref.Cells(i, 14).value
    'ws_clarity.Cells(i, 10).value = ws_ref.Cells(i, 15).value
    'ws_clarity.Cells(i, 11).value = ws_ref.Cells(i, 16).value
    'ws_clarity.Cells(i, 12).value = ws_ref.Cells(i, 17).value
    'ws_clarity.Cells(i, 13).value = ws_ref.Cells(i, 18).value
    'ws_clarity.Cells(i, 14).value = ws_ref.Cells(i, 19).value
    'ws_clarity.Cells(i, 15).value = ws_ref.Cells(i, 20).value
    'ws_clarity.Cells(i, 16).value = ws_ref.Cells(i, 21).value
    'ws_clarity.Cells(i, 17).value = ws_ref.Cells(i, 22).value
    'ws_clarity.Cells(i, 18).value = ws_ref.Cells(i, 23).value
    'ws_clarity.Cells(i, 19).value = ws_ref.Cells(i, 24).value
    'ws_clarity.Cells(i, 20).value = ws_ref.Cells(i, 25).value
    'getting all the weeks for the pi
    lastColumn_ws_ref = ws_ref.Cells(1, ws_ref.Columns.count).End(-4159).Column
    a = 9
    For j = 14 To lastColumn_ws_ref - 1
        ws_clarity.Cells(1, a).value = ws_ref.Cells(1, j).value
        a = a + 1
    Next j




    ' Create a Dictionary to store unique results




    Set uniqueResults = CreateObject("Scripting.Dictionary")

    lastRow_ws_sum1 = ws_sum1.Cells(ws_sum1.Rows.count, 1).End(-4162).Row ' -4162 is equivalent to xlUp
    lastRow_ws_team = ws_Teams.Cells(ws_Teams.Rows.count, 1).End(-4162).Row ' -4162 is equivalent to xlUp
    lastRow_ws_itpr = ws_itpr.Cells(ws_itpr.Rows.count, 1).End(-4162).Row ' -4162 is equivalent to xlUp


    resultfRow = 2
    For i = 2 To lastRow_ws_team
        searchteammem = ws_Teams.Cells(i, 7).value
        'MsgBox searchteammem        'getting the team member
        searchteam = ws_Teams.Cells(i, 1).value

       'MsgBox searchteam           'getting the team for team member
        uniqueResults.RemoveAll
        For j = 2 To lastRow_ws_sum1
            If ws_sum1.Cells(j, 1).value = searchteam Then
                resultitpr = ws_sum1.Cells(j, 4).value
               ' MsgBox resultitpr


                If Not uniqueResults.Exists(resultitpr) Then
                    uniqueResults.Add resultitpr, Nothing
                End If
                resultfeature = ws_sum1.Cells(j, 2).value
                'MsgBox resultfeature
            End If
        Next j



        For Each resultitpr In uniqueResults.Keys
            'MsgBox resultitpr
            ws_clarity.Cells(resultfRow, 2).value = resultitpr ' Write the unique result for Epic with theme to the next column
            ws_clarity.Cells(resultfRow, 1).value = searchteam
            ws_clarity.Cells(resultfRow, 6).value = ws_Teams.Cells(i, 2).value  ' assigning name in clarity from teammember
            ws_clarity.Cells(resultfRow, 7).value = ws_Teams.Cells(i, 3).value  ' assigning email in clarity from teammember
            ws_clarity.Cells(resultfRow, 8).value = ws_Teams.Cells(i, 4).value  ' assigning location in clarity from teammember


            'Trimming the iTPR without Theme
                colonPosition = InStr(resultitpr, ":")
                            ' Check if the colon was found
                            If colonPosition > 0 Then
                            ' Extract the substring from the start to the position before the colon
                                resultString = Mid(resultitpr, colonPosition + 2)
                                resultString = Trim(resultString)
                                'MsgBox resultString
                            Else
                                ' If no colon is found, return the entire string
                                resultString = resultitpr
                            End If
                'MsgBox resultString
                ws_clarity.Cells(resultfRow, 3).value = resultString ' Write the unique result for Epic without theme to the next column
                'lookup for ITPR owner
                Owner = VLookup(resultString, ws_itpr, 3, 2)
                ws_clarity.Cells(resultfRow, 4).value = Owner  ' assigning owner for ITPR in clarity from reference
            resultfRow = resultfRow + 1


         Next
            ' If no matches were found, you can optionally write "Not Found"
            If uniqueResults.count = 0 Then
                ws_clarity.Cells(resultfRow, 2).value = "Not Found"
            End If

        'MsgBox searchteammem
        role = VLookup(searchteammem, ws_Teams, 5, 2)
        'MsgBox role

        'MsgBox role
        If role = "Engineering Lead" Then
            string1 = "Additional ITPR for Leaders"
            'MsgBox string1
            'For x = 2 To lastRow_ws_itpr
                additional_itpr = VLookup(string1, ws_itpr, 2, 4)
                'MsgBox additional_itpr
               ' If itpr_type = "Additional Core for Leaders " Then
                    ws_clarity.Cells(resultfRow, 2).value = additional_itpr
                    ws_clarity.Cells(resultfRow, 3).value = additional_itpr
                    ws_clarity.Cells(resultfRow, 1).value = searchteam
                    ws_clarity.Cells(resultfRow, 6).value = ws_Teams.Cells(i, 2).value  ' assigning name in clarity from teammember
                    ws_clarity.Cells(resultfRow, 7).value = ws_Teams.Cells(i, 3).value  ' assigning email in clarity from teammember
                    ws_clarity.Cells(resultfRow, 8).value = ws_Teams.Cells(i, 4).value  ' assigning location in clarity from teammember
                    Owner = VLookup(additional_itpr, ws_itpr, 3, 2)
                    ws_clarity.Cells(resultfRow, 4).value = Owner  ' assigning owner for ITPR in clarity from reference
                'End If
            resultfRow = resultfRow + 1
            'Next
        End If

    Next i


End Function



Function ClaritySheet_l(ws_clarity_l, ws_ref, ws_Teams, ws_sum1, ws_itpr)
   ws_clarity_l.Cells.ClearContents
    'MsgBox "her in claritysheet"
    Dim uniqueValues As Collection
    i = 1
    ws_clarity_l.Cells(i, 1).value = "Team"
    ws_clarity_l.Cells(i, 2).value = "Initiative with THEME"
    ws_clarity_l.Cells(i, 3).value = "Initiative (Use Dropdown of Current ITPRs)"
    ws_clarity_l.Cells(i, 4).value = "PMO Owner"
    ws_clarity_l.Cells(i, 5).value = "Missing from Clarity assingment"
    ws_clarity_l.Cells(i, 6).value = "Resource Name (in Clarity)"
    ws_clarity_l.Cells(i, 7).value = "Network ID or email Location"
    ws_clarity_l.Cells(i, 8).value = "Location"
    'ws_clarity_l.Cells(i, 9).value = ws_ref.Cells(i, 14).value
    'ws_clarity_l.Cells(i, 10).value = ws_ref.Cells(i, 15).value
    'ws_clarity_l.Cells(i, 11).value = ws_ref.Cells(i, 16).value
    'ws_clarity_l.Cells(i, 12).value = ws_ref.Cells(i, 17).value
    'ws_clarity_l.Cells(i, 13).value = ws_ref.Cells(i, 18).value
    'ws_clarity_l.Cells(i, 14).value = ws_ref.Cells(i, 19).value
    'ws_clarity_l.Cells(i, 15).value = ws_ref.Cells(i, 20).value
    'ws_clarity_l.Cells(i, 16).value = ws_ref.Cells(i, 21).value
    'ws_clarity_l.Cells(i, 17).value = ws_ref.Cells(i, 22).value
    'ws_clarity_l.Cells(i, 18).value = ws_ref.Cells(i, 23).value
    'ws_clarity_l.Cells(i, 19).value = ws_ref.Cells(i, 24).value
    'ws_clarity_l.Cells(i, 20).value = ws_ref.Cells(i, 25).value
    'getting all the weeks for the pi
    lastColumn_ws_ref = ws_ref.Cells(1, ws_ref.Columns.count).End(-4159).Column
    a = 9
    For j = 14 To lastColumn_ws_ref - 1
        ws_clarity_l.Cells(1, a).value = ws_ref.Cells(1, j).value
        a = a + 1
    Next j


    ' Create a Dictionary to store unique results
    Set uniqueResults = CreateObject("Scripting.Dictionary")

    lastRow_ws_sum1 = ws_sum1.Cells(ws_sum1.Rows.count, 1).End(-4162).Row ' -4162 is equivalent to xlUp
    lastRow_ws_team = ws_Teams.Cells(ws_Teams.Rows.count, 1).End(-4162).Row ' -4162 is equivalent to xlUp
    lastRow_ws_itpr = ws_itpr.Cells(ws_itpr.Rows.count, 1).End(-4162).Row ' -4162 is equivalent to xlUp


    resultfRow = 2
    For i = 2 To lastRow_ws_team
        searchteammem = ws_Teams.Cells(i, 7).value
        'MsgBox searchteammem        'getting the team member
        searchteam = ws_Teams.Cells(i, 1).value
            If searchteam = "All train" Then
               searchteammem = ws_Teams.Cells(i, 2).value
               role = ws_Teams.Cells(i, 5).value
               'MsgBox searchteammem
               uniqueResults.RemoveAll
               For j = 2 To lastRow_ws_sum1
                   resultitpr = ws_sum1.Cells(j, 4).value
                    If Not uniqueResults.Exists(resultitpr) Then
                       uniqueResults.Add resultitpr, Nothing
                    End If
               Next j
               For Each resultitpr In uniqueResults.Keys
                    'MsgBox resultitpr
                    ws_clarity_l.Cells(resultfRow, 2).value = resultitpr ' Write the unique result for Epic with theme to the next column
                    ws_clarity_l.Cells(resultfRow, 1).value = searchteam
                    ws_clarity_l.Cells(resultfRow, 6).value = ws_Teams.Cells(i, 2).value  ' assigning name in clarity from teammember
                    ws_clarity_l.Cells(resultfRow, 7).value = ws_Teams.Cells(i, 3).value  ' assigning email in clarity from teammember
                    ws_clarity_l.Cells(resultfRow, 8).value = ws_Teams.Cells(i, 4).value  ' assigning location in clarity from teammember
                    'Trimming the iTPR without Theme
                        colonPosition = InStr(resultitpr, ":")
                                    ' Check if the colon was found
                                    If colonPosition > 0 Then
                                    ' Extract the substring from the start to the position before the colon
                                        resultString = Mid(resultitpr, colonPosition + 2)
                                        resultString = Trim(resultString)
                                        'MsgBox resultString
                                    Else
                                        ' If no colon is found, return the entire string
                                        resultString = resultitpr
                                    End If
                        'MsgBox resultString
                        ws_clarity_l.Cells(resultfRow, 3).value = resultString ' Write the unique result for Epic without theme to the next column
                        'lookup for ITPR owner
                        Owner = VLookup(resultString, ws_itpr, 3, 2)
                        ws_clarity_l.Cells(resultfRow, 4).value = Owner  ' assigning owner for ITPR in clarity from reference
                    resultfRow = resultfRow + 1
                Next
            End If
            role1 = VLookup(searchteammem, ws_Teams, 5, 2)
            'MsgBox role1
            If role = "Train_lead" Then
                string1 = "Additional ITPR for Leaders"
                'MsgBox string1
                'For x = 2 To lastRow_ws_itpr
                additional_itpr = VLookup(string1, ws_itpr, 2, 4)
                'MsgBox additional_itpr
               ' If itpr_type = "Additional Core for Leaders " Then
                    ws_clarity_l.Cells(resultfRow, 2).value = additional_itpr
                    ws_clarity_l.Cells(resultfRow, 3).value = additional_itpr
                    ws_clarity_l.Cells(resultfRow, 1).value = searchteam
                    ws_clarity_l.Cells(resultfRow, 6).value = ws_Teams.Cells(i, 2).value  ' assigning name in clarity from teammember
                    ws_clarity_l.Cells(resultfRow, 7).value = ws_Teams.Cells(i, 3).value  ' assigning email in clarity from teammember
                    ws_clarity_l.Cells(resultfRow, 8).value = ws_Teams.Cells(i, 4).value  ' assigning location in clarity from teammember
                    Owner = VLookup(additional_itpr, ws_itpr, 3, 2)
                    ws_clarity_l.Cells(resultfRow, 4).value = Owner  ' assigning owner for ITPR in clarity from reference
                'End If
                'Next
                resultfRow = resultfRow + 1
            End If





    Next i


End Function


Function VLookup(lookupValue, lookupSheet, returnColumn, searchColumn)
    Dim lastRow, j
    lastRow = lookupSheet.Cells(lookupSheet.Rows.count, searchColumn).End(-4162).Row ' Find the last row in the search column

    ' Loop through the rows in the lookup range
    For j = 2 To lastRow ' Assuming data starts from row 2
        If lookupSheet.Cells(j, searchColumn).value = lookupValue Then
            VLookup = lookupSheet.Cells(j, returnColumn).value ' Return the corresponding value from the return column
            Exit Function
        End If
    Next j

    VLookup = "" ' Return empty if not found
End Function


Function VLookup1(lookupValue, lookupSheet, returnColumn, searchColumn)
    Dim lastRow, j
    lastRow = lookupSheet.Cells(lookupSheet.Rows.count, searchColumn).End(-4162).Row ' Find the last row in the search column

    ' Loop through the rows in the lookup range
    ' Loop through the rows in the lookup range
    For j = 2 To lastRow ' Assuming data starts from row 2
        ' Use Trim to remove any leading or trailing spaces
        If Trim(lookupSheet.Cells(j, searchColumn).Value2) = Trim(lookupValue) Then
            Dim rawValue As Variant
            rawValue = lookupSheet.Cells(j, returnColumn).Value2 ' Get the raw value

            ' Check if the raw value is a percentage (stored as a decimal)
            If VarType(rawValue) = vbDouble Then
                ' If it's a percentage (e.g., 100% is stored as 1), convert to whole number
                If rawValue < 1 Then
                    VLookup1 = rawValue * 100 ' Convert to percentage
                Else
                    VLookup1 = rawValue ' Return as is if it's a whole number
                End If
            Else
                ' If it's a string, check for percentage sign
                If InStr(1, CStr(rawValue), "%") > 0 Then
                    ' Remove the percentage sign and convert to number
                    VLookup1 = Val(Replace(CStr(rawValue), "%", "")) ' Convert to number
                Else
                    ' Otherwise, just return the raw value
                    VLookup1 = Val(rawValue) ' Convert to number
                End If
            End If

            ' Ensure that if the value is a percentage, we return it as a whole number
            If VLookup1 < 1 And VLookup1 >= 0 Then
                VLookup1 = VLookup1 * 100 ' Convert to whole number percentage
            End If

            Exit Function
        End If
    Next j

    VLookup1 = "" ' Return empty if not found
End Function

Function VLookupMultiCriteria(lookupValues As Variant, lookupSheet As Worksheet, returnColumn As Integer, searchColumns As Variant) As Variant
    Dim lastRow As Long
    Dim j As Long
    Dim matchFound As Boolean
    Dim i As Long

    lastRow = lookupSheet.Cells(lookupSheet.Rows.count, searchColumns(0)).End(xlUp).Row ' Find the last row in the first search column

    ' Loop through the rows in the lookup range
    For j = 2 To lastRow ' Assuming data starts from row 2
        matchFound = True ' Assume a match is found until proven otherwise

        ' Check each search column for the corresponding lookup value
        For i = LBound(lookupValues) To UBound(lookupValues)
            If lookupSheet.Cells(j, searchColumns(i)).value <> lookupValues(i) Then
                matchFound = False ' If any criteria do not match, set matchFound to False
                Exit For
            End If
        Next i

        ' If all criteria match, return the corresponding value from the return column
        If matchFound Then
            VLookupMultiCriteria = lookupSheet.Cells(j, returnColumn).value
            Exit Function
        End If
    Next j

    VLookupMultiCriteria = "" ' Return empty if not found
End Function



' Custom SUMIFS function with 2 criteria
Function SumIfs(dataSheet, lastRow, sumColumn, criteria1, criteriaColumn1, criteria2, criteriaColumn2)
    Dim i, total
    total = 0

    ' Loop through each row in the data sheet
    For i = 2 To lastRow ' Assuming data starts from row 2
        ' Check if the criteria match
        If dataSheet.Cells(i, criteriaColumn1).value = criteria1 And _
           dataSheet.Cells(i, criteriaColumn2).value = criteria2 Then
            total = total + dataSheet.Cells(i, sumColumn).value ' Sum the values
        End If
    Next i

    SumIfs = total ' Return the total sum
End Function


' Custom SUMIFS function with 1 criteria
Function SumIfs2(dataSheet, lastRow, sumColumn, criteria1, criteriaColumn1)
    Dim i, total
    total = 0

    ' Loop through each row in the data sheet
    For i = 2 To lastRow ' Assuming data starts from row 2
        ' Check if the criteria match
        If dataSheet.Cells(i, criteriaColumn1).value = criteria1 Then

            total = total + dataSheet.Cells(i, sumColumn).value ' Sum the values
        End If
    Next i

    SumIfs2 = total ' Return the total sum
End Function


' Custom SUMIFS function with multiple criteria
Function SumIfs3(dataSheet, lastRow, sumColumn, criteria1, criteriaColumn1, criteria2, criteriaColumn2, criteria3, criteriaColumn3, criteria4, criteriaColumn4)
    Dim i, total
    total = 0

    ' Loop through each row in the data sheet
    For i = 2 To lastRow ' Assuming data starts from row 2
        ' Check if the criteria match
        If dataSheet.Cells(i, criteriaColumn1).value = criteria1 And _
           dataSheet.Cells(i, criteriaColumn2).value = criteria2 And _
           dataSheet.Cells(i, criteriaColumn3).value = criteria3 And _
           dataSheet.Cells(i, criteriaColumn4).value = criteria4 Then


            total = total + dataSheet.Cells(i, sumColumn).value ' Sum the values
        End If
    Next i

    SumIfs3 = total ' Return the total sum
End Function


' Custom SUMIFS function with 3 criteria
Function SumIfs4(dataSheet, lastRow, sumColumn, criteria1, criteriaColumn1, criteria2, criteriaColumn2, criteria3, criteriaColumn3)
    Dim i, total
    total = 0

    ' Loop through each row in the data sheet
    For i = 2 To lastRow ' Assuming data starts from row 2
        ' Check if the criteria match
        If dataSheet.Cells(i, criteriaColumn1).value = criteria1 And _
           dataSheet.Cells(i, criteriaColumn2).value = criteria2 And _
           dataSheet.Cells(i, criteriaColumn3).value = criteria3 Then
            total = total + dataSheet.Cells(i, sumColumn).value ' Sum the values
        End If
    Next i

    SumIfs4 = total ' Return the total sum
End Function


Function SumIfs10(dataSheet, lastRow, sumColumn, criteria1, criteriaColumn1)
    Dim i, sumResult
    sumResult = 0 ' Initialize the sum result

    ' Loop through each row
    For i = 1 To lastRow
        ' Check if the first criteria (team name) is met
        If Trim(dataSheet.Cells(i, criteriaColumn1).value) = criteria1 Then
            ' Attempt to convert the value in the sum column to a number
            Dim cellValue
            cellValue = CStr(dataSheet.Cells(i, sumColumn).value)
            'MsgBox cellValue
            ' Check if the value is numeric
            If IsNumeric(cellValue) Then
                ' If the value is a percentage, convert it to a whole number
                If InStr(1, dataSheet.Cells(i, sumColumn).Text, "%") > 0 Then
                    cellValue = cellValue * 100 ' Convert percentage to whole number
                   ' MsgBox cellValue
                End If


            ' Add the numeric value to the sum result
            sumResult = sumResult + cellValue
            End If
        Else
            ' Debug output for non-matching criteria
            'WScript.Echo "Criteria not matched: " & dataSheet.Cells(i, criteriaColumn1).value
        End If
    Next i

    ' Return the total sum
    SumIfs10 = sumResult
End Function


' Function to count rows that 1  criteria
Function CountIfs1(dataSheet, lastRow, criteria1, criteriaColumn1)
    Dim count, i
    count = 0 ' Initialize count
    'MsgBox criteria1
    'MsgBox criteriaColumn1
    ' Loop through the data range
    For i = 2 To lastRow
        ' Check if the criteria are met
        If dataSheet.Cells(i, criteriaColumn1).value = criteria1 Then

            count = count + 1 ' Increment count if criteria are met
        End If
    Next

    CountIfs1 = count ' Return the count
End Function

' Function to count rows that 2  criteria
Function CountIfs2(dataSheet, lastRow, criteria1, criteriaColumn1, criteria2, criteriaColumn2)
    Dim count, i
    count = 0 ' Initialize count
    'MsgBox criteria1
    'MsgBox criteriaColumn1
    ' Loop through the data range
    For i = 2 To lastRow
        ' Check if the criteria are met
        If dataSheet.Cells(i, criteriaColumn1).value = criteria1 And _
            dataSheet.Cells(i, criteriaColumn2).value = criteria2 Then

            count = count + 1 ' Increment count if criteria are met
        End If
    Next

    CountIfs2 = count ' Return the count
End Function







'Function for creating clarity by sprint planning
Function ClaritySheet1(ws_clarity1, ws_ref, ws_Teams, ws_sum1, ws_itpr)
   'ws_clarity1.Cells.ClearContents
    'MsgBox "her in claritysheet for sprint"
    Dim uniqueValues As Collection
    i = 1
    ws_clarity1.Cells(i, 1).value = "Team"
    ws_clarity1.Cells(i, 2).value = "Initiative with THEME"
    ws_clarity1.Cells(i, 3).value = "Initiative (Use Dropdown of Current ITPRs)"
    ws_clarity1.Cells(i, 4).value = "PMO Owner"
    ws_clarity1.Cells(i, 5).value = "Missing from Clarity assingment"
    ws_clarity1.Cells(i, 6).value = "Resource Name (in Clarity)"
    ws_clarity1.Cells(i, 7).value = "Network ID or email Location"
    ws_clarity1.Cells(i, 8).value = "Location"
    ws_clarity1.Cells(i, 9).value = ws_ref.Cells(2, 28).value
    ws_clarity1.Cells(i, 10).value = ws_ref.Cells(3, 28).value
    ws_clarity1.Cells(i, 11).value = Left((ws_ref.Cells(4, 28).value), 9)
    ws_clarity1.Cells(i, 12).value = ws_ref.Cells(4, 28).value
    ws_clarity1.Cells(i, 13).value = ws_ref.Cells(5, 28).value
    ws_clarity1.Cells(i, 14).value = ws_ref.Cells(6, 28).value
    ws_clarity1.Cells(i, 15).value = Left((ws_ref.Cells(7, 28).value), 9)
    ws_clarity1.Cells(i, 16).value = ws_ref.Cells(7, 28).value
    ws_clarity1.Cells(i, 17).value = ws_ref.Cells(8, 28).value
    ws_clarity1.Cells(i, 18).value = ws_ref.Cells(9, 28).value
    ws_clarity1.Cells(i, 19).value = Left((ws_ref.Cells(10, 28).value), 9)
    ws_clarity1.Cells(i, 20).value = ws_ref.Cells(10, 28).value
    ws_clarity1.Cells(i, 21).value = ws_ref.Cells(11, 28).value
    ws_clarity1.Cells(i, 22).value = ws_ref.Cells(12, 28).value
    ws_clarity1.Cells(i, 23).value = Left((ws_ref.Cells(13, 28).value), 9)
    ws_clarity1.Cells(i, 24).value = ws_ref.Cells(13, 28).value
    ws_clarity1.Cells(i, 25).value = ws_ref.Cells(14, 28).value
    ws_clarity1.Cells(i, 26).value = ws_ref.Cells(15, 28).value
    ws_clarity1.Cells(i, 27).value = Left((ws_ref.Cells(16, 28).value), 9)
    ws_clarity1.Cells(i, 28).value = ws_ref.Cells(16, 28).value
    ws_clarity1.Cells(i, 29).value = ws_ref.Cells(17, 28).value
    ws_clarity1.Cells(i, 30).value = ws_ref.Cells(18, 28).value
    ws_clarity1.Cells(i, 31).value = "2025.PI3.S1"
    ws_clarity1.Cells(i, 32).value = "2025.PI3.S2"
    ws_clarity1.Cells(i, 33).value = "2025.PI3.S3"
    ws_clarity1.Cells(i, 34).value = "2025.PI3.S4"
    ws_clarity1.Cells(i, 35).value = "2025.PI3.S5"


    ' Create a Dictionary to store unique results
    Set uniqueResults = CreateObject("Scripting.Dictionary")

    lastRow_ws_sum1 = ws_sum1.Cells(ws_sum1.Rows.count, 1).End(-4162).Row ' -4162 is equivalent to xlUp
    lastRow_ws_team = ws_Teams.Cells(ws_Teams.Rows.count, 1).End(-4162).Row ' -4162 is equivalent to xlUp
    lastRow_ws_itpr = ws_itpr.Cells(ws_itpr.Rows.count, 1).End(-4162).Row ' -4162 is equivalent to xlUp


    resultfRow = 2
    For i = 2 To lastRow_ws_team
        searchteammem = ws_Teams.Cells(i, 7).value
        'MsgBox searchteammem        'getting the team member
        searchteam = ws_Teams.Cells(i, 1).value

       'MsgBox searchteam           'getting the team for team member
        uniqueResults.RemoveAll
        For j = 2 To lastRow_ws_sum1
            If ws_sum1.Cells(j, 1).value = searchteam Then
                resultitpr = ws_sum1.Cells(j, 4).value
                'MsgBox resultitpr


                If Not uniqueResults.Exists(resultitpr) Then
                    uniqueResults.Add resultitpr, Nothing
                End If
                resultfeature = ws_sum1.Cells(j, 2).value
               ' MsgBox resultfeature
            End If
        Next j



        For Each resultitpr In uniqueResults.Keys
            'MsgBox resultitpr
            'MsgBox "inside unique"
            ws_clarity1.Cells(resultfRow, 2).value = resultitpr ' Write the unique result for Epic with theme to the next column
            ws_clarity1.Cells(resultfRow, 1).value = searchteam
            ws_clarity1.Cells(resultfRow, 6).value = ws_Teams.Cells(i, 2).value  ' assigning name in clarity from teammember
            ws_clarity1.Cells(resultfRow, 7).value = ws_Teams.Cells(i, 3).value  ' assigning email in clarity from teammember
            ws_clarity1.Cells(resultfRow, 8).value = ws_Teams.Cells(i, 4).value  ' assigning location in clarity from teammember


            'Trimming the iTPR without Theme
                colonPosition = InStr(resultitpr, ":")
                            ' Check if the colon was found
                            If colonPosition > 0 Then
                            ' Extract the substring from the start to the position before the colon
                                resultString = Mid(resultitpr, colonPosition + 2)
                                resultString = Trim(resultString)
                                'MsgBox resultString
                            Else
                                ' If no colon is found, return the entire string
                                resultString = resultitpr
                            End If
                'MsgBox resultString
                ws_clarity1.Cells(resultfRow, 3).value = resultString ' Write the unique result for Epic without theme to the next column
                'lookup for ITPR owner
                Owner = VLookup(resultString, ws_itpr, 3, 2)
                ws_clarity1.Cells(resultfRow, 4).value = Owner  ' assigning owner for ITPR in clarity from reference
            resultfRow = resultfRow + 1


         Next
            ' If no matches were found, you can optionally write "Not Found"
            If uniqueResults.count = 0 Then
                ws_clarity1.Cells(resultfRow, 2).value = "Not Found"
            End If

        'MsgBox searchteammem
        role = VLookup(searchteammem, ws_Teams, 5, 2)
        'MsgBox role

        'MsgBox role
        If role = "Engineering Lead" Then
            string1 = "Additional ITPR for Leaders"
            'MsgBox string1
            'For x = 2 To lastRow_ws_itpr
                additional_itpr = VLookup(string1, ws_itpr, 2, 4)
                'MsgBox additional_itpr
               ' If itpr_type = "Additional Core for Leaders " Then
                    ws_clarity1.Cells(resultfRow, 2).value = additional_itpr
                    ws_clarity1.Cells(resultfRow, 3).value = additional_itpr
                    ws_clarity1.Cells(resultfRow, 1).value = searchteam
                    ws_clarity1.Cells(resultfRow, 6).value = ws_Teams.Cells(i, 2).value  ' assigning name in clarity from teammember
                    ws_clarity1.Cells(resultfRow, 7).value = ws_Teams.Cells(i, 3).value  ' assigning email in clarity from teammember
                    ws_clarity1.Cells(resultfRow, 8).value = ws_Teams.Cells(i, 4).value  ' assigning location in clarity from teammember
                    Owner = VLookup(additional_itpr, ws_itpr, 3, 2)
                    ws_clarity1.Cells(resultfRow, 4).value = Owner  ' assigning owner for ITPR in clarity from reference
                'End If
            resultfRow = resultfRow + 1
            'Next
        End If

    Next i


End Function


