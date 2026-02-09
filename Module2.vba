Sub Sprint_ClarityWeek()
    Dim sprint_start As Variant
    Dim Release As Variant
    Dim ws_ref As Worksheet
    Dim weekNum
    Dim weekDaysCount
    Dim weekCounts
    Set ws_ref = ThisWorkbook.Sheets("Reference")
    Set ws_sum1 = ThisWorkbook.Sheets("Summary")


    sprint_start = ws_ref.Range("I3").value
    'MsgBox sprint_start
    Release = ws_ref.Range("I2").value
    sprints = ws_ref.Range("I4").value
    ws_ref.Range("K2").value = "Sprint Start Date"
    ws_ref.Range("L2").value = "Sprint End Date"
    ws_ref.Range("M2").value = "Rally ID"
    'ws_ref.Range("N2").Value = "Sprint starting week"
    'ws_ref.Range("O2").Value = "Sprint ending week"
    ws_ref.Range("M1").value = "Clarity Week"

    ' Convert the input string to a date
    sprint_start = CDate(sprint_start)

   ' Loop to calculate sprints
    x = 3
    y = 10
    a = 1
    b = 14
    c = 8
    For i = 0 To sprints

    ' Calculate the end date for the sprint (10 days after the start date)
        'MsgBox sprint_start

        ws_ref.Cells(x, y).value = "Sprint " & a
        ws_ref.Cells(x, y + 1).value = sprint_start

        sprintEndDate = DateAdd("d", 13, sprint_start)
        ws_ref.Cells(x, y + 2).value = sprintEndDate
        'MsgBox sprintEndDate

        ws_ref.Cells(x, y + 3).value = Release & ".S" & a

        ' Calculate the week with start and end dates
        'MsgBox sprint_start
            weekStartDate = DateAdd("d", -Weekday(sprint_start) + 2, sprint_start) ' Start of the week (Monday)
            'ws_ref.Cells(x, y + 4).Value = weekStartDate
            'MsgBox b
            ws_ref.Cells(1, b).value = weekStartDate

            b = b + 1
            middleweek = DateAdd("d", 7, weekStartDate)
            'ws_ref.Cells(x, y + 5).value = middleweek
            ws_ref.Cells(1, b).value = middleweek

            'MsgBox b
            weekEndDate = DateAdd("d", -Weekday(sprint_start) + 3, sprintEndDate)
            'ws_ref.Cells(1, b).value = weekEndDate
            'weekEndDate = DateAdd("d", 6, weekStartDate) ' End of the week (Sunday)
            'ws_ref.Cells(x, y + 5).Value = weekStartDate
            'MsgBox sprint_start
           'weekNum = DatePart("ww", sprint_start, vbMonday, vbFirstFourDays)
            'MsgBox weekNum
            'ws_ref.Cells(x, y + 6).Value = weekNum



        sprint_start = sprintEndDate + 1
        x = x + 1 ' Move to the next row
        a = a + 1 ' Increment the sprint number
        b = b + 1
        c = c + 1
        'MsgBox b

    Next i

    MsgBox "Completed"
End Sub